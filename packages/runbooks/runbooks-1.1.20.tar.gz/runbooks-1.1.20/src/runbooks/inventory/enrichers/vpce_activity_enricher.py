#!/usr/bin/env python3
"""
VPC Endpoint Activity Enricher - VPC Endpoint Health Signals (V1-V5)

Analyzes VPC Endpoint activity patterns using CloudWatch metrics and dependency
analysis to identify underutilized or idle endpoints for cost optimization.

Decommission Signals (V1-V5):
- V1: Zero data transfer (40 points) - No BytesIn/BytesOut for 90+ days
- V2: No service dependencies (20 points) - Zero resources using endpoint
- V3: Interface endpoints with 1 interface only (10 points) - Minimal configuration
- V4: Non-production VPC (5 points) - Environment tags indicate dev/test/staging
- V5: Age >180 days unused (25 points) - Old endpoint with zero transfer

Pattern: Reuses ALB enricher structure (KISS/DRY/LEAN) + VPCEndpointDependencyMapper delegation

Strategic Alignment:
- Objective 1 (runbooks package): Reusable VPC Endpoint enrichment
- Enterprise SDLC: Cost optimization with evidence-based signals
- KISS/DRY/LEAN: Single enricher, CloudWatch consolidation, dependency delegation

Usage:
    from runbooks.inventory.enrichers.vpce_activity_enricher import VPCEActivityEnricher

    enricher = VPCEActivityEnricher(
        operational_profile='${CENTRALISED_OPS_PROFILE}',
        region='ap-southeast-2'
    )

    enriched_df = enricher.enrich_vpce_activity(discovery_df)

    # Adds columns:
    # - bytes_in_90d: Sum of BytesIn over 90 days
    # - bytes_out_90d: Sum of BytesOut over 90 days
    # - dependency_count: Number of resources using endpoint
    # - interface_count: Number of network interfaces
    # - vpc_environment: VPC environment tag (prod/nonprod/dev/test/staging)
    # - age_days: Days since endpoint creation
    # - v1_signal: Boolean (zero data transfer)
    # - v2_signal: Boolean (no dependencies)
    # - v3_signal: Boolean (minimal interfaces)
    # - v4_signal: Boolean (non-production VPC)
    # - v5_signal: Boolean (age >180 days unused)
    # - cloudwatch_enrichment_success: Boolean (enrichment succeeded)
    # - enrichment_status: String (SUCCESS/FAILED/PENDING)
    # - enrichment_error: String (error message if failed)
    # - decommission_score: Total score (0-100 scale)
    # - decommission_tier: MUST/SHOULD/COULD/KEEP/UNKNOWN
    # - total_possible_score: Maximum achievable score (60 or 100)

Author: Runbooks Team
Version: 1.0.0
Epic: v1.1.20 FinOps Dashboard Enhancements
Track: Track 16 - VPC Endpoint Activity Enrichment
"""

import pandas as pd
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from runbooks.common.profile_utils import (
    get_profile_for_operation,
    create_operational_session,
    create_timeout_protected_client
)
from runbooks.common.rich_utils import (
    print_info, print_success, print_warning, print_error,
    create_progress_bar, console
)
from runbooks.common.output_controller import OutputController
from runbooks.vpc.endpoint_dependency_mapper import VPCEndpointDependencyMapper

logger = logging.getLogger(__name__)

# VPC Endpoint signal weights (0-100 scale)
DEFAULT_VPCE_WEIGHTS = {
    'V1': 40,  # Zero data transfer 90+ days (aligns with EC2 E1/S3 S1)
    'V2': 20,  # No service dependencies
    'V3': 10,  # Interface endpoints with 1 interface only
    'V4': 5,   # Non-production VPC
    'V5': 25   # Age >180 days unused (Manager's age emphasis for VPC)
}


class VPCEActivityEnricher:
    """
    VPC Endpoint activity enrichment using CloudWatch metrics for V1-V5 decommission signals.

    Consolidates CloudWatch VPCEndpoint metrics into actionable decommission signals:
    - BytesIn/BytesOut (V1: zero data transfer)
    - VPCEndpointDependencyMapper delegation (V2: no dependencies)
    - NetworkInterfaceIds count (V3: minimal interfaces)
    - VPC environment tags (V4: non-production)
    - CreationTimestamp + zero transfer (V5: age unused)
    """

    def __init__(
        self,
        operational_profile: str,
        region: str = "ap-southeast-2",
        output_controller: Optional[OutputController] = None,
        lookback_days: int = 90
    ):
        """
        Initialize VPC Endpoint activity enricher.

        Args:
            operational_profile: AWS profile for CloudWatch API access
            region: AWS region for API calls (default: ap-southeast-2)
            output_controller: OutputController for verbose output (optional)
            lookback_days: CloudWatch metrics lookback period (default: 90 days)

        Profile Requirements:
            - cloudwatch:GetMetricStatistics (VPCEndpoint namespace metrics)
            - ec2:DescribeVpcEndpoints (endpoint metadata)
            - ec2:DescribeVpcs (VPC environment tags)
        """
        resolved_profile = get_profile_for_operation("operational", operational_profile)
        self.session = create_operational_session(resolved_profile)
        self.cloudwatch = create_timeout_protected_client(self.session, 'cloudwatch', region_name=region)
        self.ec2 = create_timeout_protected_client(self.session, 'ec2', region_name=region)

        self.region = region
        self.profile = resolved_profile
        self.output_controller = output_controller or OutputController()
        self.lookback_days = lookback_days

        # Initialize VPCEndpointDependencyMapper (DRY - reuse existing code)
        self.dependency_mapper = VPCEndpointDependencyMapper(
            profile=resolved_profile,
            region=region
        )

        if self.output_controller.verbose:
            print_info(f"🔍 VPCEActivityEnricher initialized: profile={resolved_profile}, region={region}")
            print_info(f"   Metrics: BytesIn, BytesOut, Dependencies, NetworkInterfaces, VPC Environment")
        else:
            logger.debug(f"VPCEActivityEnricher initialized: profile={resolved_profile}, region={region}")

    def enrich_vpce_activity(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich VPC Endpoint DataFrame with V1-V5 activity signals.

        Args:
            df: DataFrame with vpc_endpoint_id column

        Returns:
            DataFrame with VPC Endpoint activity columns and decommission signals

        Columns Added:
            - bytes_in_90d: Sum of BytesIn over 90 days
            - bytes_out_90d: Sum of BytesOut over 90 days
            - dependency_count: Number of resources using endpoint
            - interface_count: Number of network interfaces
            - vpc_environment: VPC environment tag (prod/nonprod/dev/test/staging)
            - age_days: Days since endpoint creation
            - v1_signal: Zero data transfer (Boolean)
            - v2_signal: No dependencies (Boolean)
            - v3_signal: Minimal interfaces (Boolean)
            - v4_signal: Non-production VPC (Boolean)
            - v5_signal: Age >365 days unused (Boolean)
            - cloudwatch_enrichment_success: Boolean (enrichment succeeded)
            - enrichment_status: String (SUCCESS/FAILED/PENDING)
            - enrichment_error: String (error message if failed)
            - decommission_score: Total score (0-100)
            - decommission_tier: MUST/SHOULD/COULD/KEEP/UNKNOWN
        """
        # Graceful degradation: skip enrichment if no VPC endpoints discovered
        if df.empty:
            if self.output_controller.verbose:
                print_warning("⚠️  VPC Endpoint enrichment skipped - no endpoints discovered")
            logger.info("VPC Endpoint enrichment skipped - empty DataFrame")
            return df

        # Prerequisite validation: check for required column
        if 'vpc_endpoint_id' not in df.columns:
            # v1.1.20: Changed to DEBUG - graceful degradation, not an error condition
            logger.debug(
                "VPC Endpoint enrichment skipped - vpc_endpoint_id column not found",
                extra={
                    "reason": "Missing required column",
                    "signal_impact": "V1-V5 signals unavailable",
                    "alternative": "Ensure VPC Endpoint discovery completed before enrichment"
                }
            )
            return df

        if self.output_controller.verbose:
            print_info(f"🔄 Starting VPC Endpoint activity enrichment for {len(df)} endpoints...")
        else:
            logger.info(f"VPC Endpoint activity enrichment started for {len(df)} endpoints")

        # Initialize activity columns with defaults
        activity_columns = {
            'bytes_in_90d': 0,
            'bytes_out_90d': 0,
            'dependency_count': 0,
            'interface_count': 0,
            'vpc_environment': 'unknown',
            'age_days': 0,
            'v1_signal': False,
            'v2_signal': False,
            'v3_signal': False,
            'v4_signal': False,
            'v5_signal': False,
            'cloudwatch_enrichment_success': False,
            'enrichment_status': 'PENDING',
            'enrichment_error': '',
            'decommission_score': 0,
            'decommission_tier': 'KEEP',
            'total_possible_score': 100
        }

        for col, default in activity_columns.items():
            if col not in df.columns:
                df[col] = default

        # Enrich each VPC Endpoint with CloudWatch metrics and dependency analysis
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=self.lookback_days)

        with create_progress_bar() as progress:
            task = progress.add_task("[cyan]CloudWatch VPC Endpoint metrics...", total=len(df))

            for idx, row in df.iterrows():
                endpoint_id = row.get('vpc_endpoint_id', '')
                vpc_id = row.get('vpc_id', '')

                if not endpoint_id or endpoint_id == 'N/A':
                    progress.update(task, advance=1)
                    continue

                try:
                    # Get VPC Endpoint metadata
                    endpoint_response = self.ec2.describe_vpc_endpoints(
                        VpcEndpointIds=[endpoint_id]
                    )

                    endpoints = endpoint_response.get('VpcEndpoints', [])
                    if not endpoints:
                        logger.debug(f"VPC Endpoint not found: {endpoint_id}")
                        df.at[idx, 'enrichment_status'] = 'FAILED'
                        df.at[idx, 'enrichment_error'] = 'Endpoint not found'
                        progress.update(task, advance=1)
                        continue

                    endpoint_metadata = endpoints[0]
                    service_name = endpoint_metadata.get('ServiceName', '').split('.')[-1]  # Extract service (s3, dynamodb, etc.)
                    creation_timestamp = endpoint_metadata.get('CreationTimestamp')
                    network_interface_ids = endpoint_metadata.get('NetworkInterfaceIds', [])

                    # V3: Interface count
                    df.at[idx, 'interface_count'] = len(network_interface_ids)

                    # V5: Age calculation
                    if creation_timestamp:
                        age_days = (datetime.now(timezone.utc) - creation_timestamp).days
                        df.at[idx, 'age_days'] = age_days

                    # V1: BytesIn (90 days)
                    bytes_in_response = self.cloudwatch.get_metric_statistics(
                        Namespace='AWS/VPCEndpoint',
                        MetricName='BytesIn',
                        Dimensions=[
                            {'Name': 'VpcEndpointId', 'Value': endpoint_id},
                            {'Name': 'ServiceName', 'Value': endpoint_metadata.get('ServiceName', '')}
                        ],
                        StartTime=start_time,
                        EndTime=end_time,
                        Period=86400,  # 1-day aggregation
                        Statistics=['Sum'],
                        Unit='Bytes'
                    )

                    bytes_in_datapoints = bytes_in_response.get('Datapoints', [])
                    if bytes_in_datapoints:
                        total_bytes_in = sum([dp['Sum'] for dp in bytes_in_datapoints])
                        df.at[idx, 'bytes_in_90d'] = int(total_bytes_in)
                        df.at[idx, 'cloudwatch_enrichment_success'] = True
                        df.at[idx, 'enrichment_status'] = 'SUCCESS'

                    # V1: BytesOut (90 days)
                    bytes_out_response = self.cloudwatch.get_metric_statistics(
                        Namespace='AWS/VPCEndpoint',
                        MetricName='BytesOut',
                        Dimensions=[
                            {'Name': 'VpcEndpointId', 'Value': endpoint_id},
                            {'Name': 'ServiceName', 'Value': endpoint_metadata.get('ServiceName', '')}
                        ],
                        StartTime=start_time,
                        EndTime=end_time,
                        Period=86400,
                        Statistics=['Sum'],
                        Unit='Bytes'
                    )

                    bytes_out_datapoints = bytes_out_response.get('Datapoints', [])
                    if bytes_out_datapoints:
                        total_bytes_out = sum([dp['Sum'] for dp in bytes_out_datapoints])
                        df.at[idx, 'bytes_out_90d'] = int(total_bytes_out)
                        df.at[idx, 'cloudwatch_enrichment_success'] = True
                        df.at[idx, 'enrichment_status'] = 'SUCCESS'

                    # V2: Dependency analysis (delegate to VPCEndpointDependencyMapper)
                    try:
                        dependency_analyses = self.dependency_mapper.analyze_endpoint_dependencies(
                            endpoint_ids=[endpoint_id]
                        )

                        if dependency_analyses:
                            dependency_count = dependency_analyses[0].dependency_count
                            df.at[idx, 'dependency_count'] = dependency_count
                    except Exception as dep_error:
                        logger.debug(
                            f"Dependency analysis failed for endpoint {endpoint_id}: {dep_error}",
                            extra={
                                "endpoint_id": endpoint_id,
                                "error_type": type(dep_error).__name__
                            }
                        )
                        # Graceful degradation: dependency_count remains 0

                    # V4: VPC environment tag
                    if vpc_id and vpc_id != 'N/A':
                        try:
                            vpc_response = self.ec2.describe_vpcs(VpcIds=[vpc_id])
                            vpcs = vpc_response.get('Vpcs', [])

                            if vpcs:
                                vpc_tags = vpcs[0].get('Tags', [])
                                for tag in vpc_tags:
                                    key = tag.get('Key', '').lower()
                                    value = tag.get('Value', '').lower()

                                    if key in ['environment', 'env']:
                                        df.at[idx, 'vpc_environment'] = value
                                        break
                        except Exception as vpc_error:
                            logger.debug(
                                f"VPC tag retrieval failed for {vpc_id}: {vpc_error}",
                                extra={
                                    "vpc_id": vpc_id,
                                    "error_type": type(vpc_error).__name__
                                }
                            )

                except Exception as e:
                    logger.warning(
                        f"CloudWatch metrics failed for VPC Endpoint {endpoint_id}: {e}",
                        extra={
                            "endpoint_id": endpoint_id,
                            "error_type": type(e).__name__,
                            "lookback_days": self.lookback_days,
                            "region": self.region
                        }
                    )
                    df.at[idx, 'enrichment_status'] = 'FAILED'
                    df.at[idx, 'enrichment_error'] = str(e)
                    pass

                progress.update(task, advance=1)

        # Calculate decommission signals and scores
        df = self._calculate_decommission_signals(df)

        metrics_found = (df['bytes_in_90d'] > 0).sum() + (df['bytes_out_90d'] > 0).sum()
        if self.output_controller.verbose:
            print_success(f"✅ VPC Endpoint enrichment complete: {metrics_found} data points collected")
        else:
            logger.info(f"VPC Endpoint enrichment complete: {metrics_found} data points collected")

        return df

    def _calculate_decommission_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate V1-V5 decommission signals and scores.

        Args:
            df: DataFrame with VPC Endpoint activity columns

        Returns:
            DataFrame with signal columns and decommission scores populated
        """
        for idx, row in df.iterrows():
            # Calculate total possible score based on signal availability
            cloudwatch_success = row.get('cloudwatch_enrichment_success', False)
            total_possible = self._calculate_total_possible_score(cloudwatch_success)
            df.at[idx, 'total_possible_score'] = total_possible

            # Check if CloudWatch enrichment succeeded
            if not cloudwatch_success:
                df.at[idx, 'decommission_score'] = 0
                df.at[idx, 'decommission_tier'] = 'UNKNOWN'
                continue  # Skip scoring for failed enrichments

            signals = {}

            # V1: Zero data transfer (50 points) - No BytesIn/BytesOut for 90+ days
            bytes_in = row.get('bytes_in_90d', 0)
            bytes_out = row.get('bytes_out_90d', 0)
            total_bytes = bytes_in + bytes_out

            if total_bytes == 0:
                df.at[idx, 'v1_signal'] = True
                signals['V1'] = DEFAULT_VPCE_WEIGHTS['V1']
            else:
                signals['V1'] = 0

            # V2: No service dependencies (25 points)
            if row.get('dependency_count', 0) == 0:
                df.at[idx, 'v2_signal'] = True
                signals['V2'] = DEFAULT_VPCE_WEIGHTS['V2']
            else:
                signals['V2'] = 0

            # V3: Interface endpoints with 1 interface only (15 points)
            if row.get('interface_count', 0) == 1:
                df.at[idx, 'v3_signal'] = True
                signals['V3'] = DEFAULT_VPCE_WEIGHTS['V3']
            else:
                signals['V3'] = 0

            # V4: Non-production VPC (5 points)
            vpc_env = row.get('vpc_environment', 'unknown').lower()
            if vpc_env in ['nonprod', 'dev', 'test', 'staging']:
                df.at[idx, 'v4_signal'] = True
                signals['V4'] = DEFAULT_VPCE_WEIGHTS['V4']
            else:
                signals['V4'] = 0

            # V5: Age >180 days unused (25 points - Manager's adjustment)
            age_days = row.get('age_days', 0)
            if age_days > 180 and total_bytes == 0:
                df.at[idx, 'v5_signal'] = True
                signals['V5'] = DEFAULT_VPCE_WEIGHTS['V5']
            else:
                signals['V5'] = 0

            # Calculate total decommission score
            total_score = sum(signals.values())
            df.at[idx, 'decommission_score'] = total_score

            # Determine decommission tier (consistent with ALB/DynamoDB/Route53)
            if total_score >= 80:
                df.at[idx, 'decommission_tier'] = 'MUST'
            elif total_score >= 50:
                df.at[idx, 'decommission_tier'] = 'SHOULD'
            elif total_score >= 25:
                df.at[idx, 'decommission_tier'] = 'COULD'
            else:
                df.at[idx, 'decommission_tier'] = 'KEEP'

        return df

    def _calculate_total_possible_score(self, cloudwatch_enrichment_success: bool) -> int:
        """
        Calculate total possible score based on signal availability.

        Implements manager's dynamic scoring denominator pattern:
        - If CloudWatch available: Score out of 100 (V1 = 40pts possible)
        - If CloudWatch unavailable: Score out of 60 (100-40, V1 removed)

        Args:
            cloudwatch_enrichment_success: Whether CloudWatch metrics were successfully retrieved

        Returns:
            Total possible score (60 or 100)

        Examples:
            >>> # CloudWatch available
            >>> self._calculate_total_possible_score(True)
            100

            >>> # CloudWatch unavailable (V1 signal removed)
            >>> self._calculate_total_possible_score(False)
            60  # 100 - 40 (V1 weight)
        """
        base_score = 100

        # V1 signal depends on CloudWatch metrics (BytesIn/Out for activity)
        if not cloudwatch_enrichment_success:
            base_score -= DEFAULT_VPCE_WEIGHTS['V1']  # Remove V1 (40pts)

        return base_score


# Export interface
__all__ = ["VPCEActivityEnricher"]

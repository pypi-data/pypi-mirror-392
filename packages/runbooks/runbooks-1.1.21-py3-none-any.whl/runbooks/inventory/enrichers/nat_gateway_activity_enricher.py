#!/usr/bin/env python3
"""
NAT Gateway Activity Enricher - NAT Gateway Health Signals (N1-N5)

Analyzes NAT Gateway activity patterns using CloudWatch metrics and availability zone
analysis to identify underutilized or idle NAT Gateways for cost optimization.

Decommission Signals (N1-N5):
- N1: Zero data transfer (40 points) - No BytesOutToDestination for 90+ days
- N2: Zero active connections (20 points) - No ActiveConnectionCount for 90+ days
- N3: Single AZ NAT Gateway (10 points) - No HA redundancy
- N4: Non-production VPC (5 points) - VPC tagged as dev/test/staging
- N5: Age >180 days (25 points) - Old NAT Gateway

Pattern: Reuses VPCE/Peering/Transit Gateway enricher structure (KISS/DRY/LEAN)

Strategic Alignment:
- Objective 1 (runbooks package): Reusable NAT Gateway enrichment
- Enterprise SDLC: Cost optimization with evidence-based signals
- KISS/DRY/LEAN: Single enricher, CloudWatch consolidation, HA validation

Usage:
    from runbooks.inventory.enrichers.nat_gateway_activity_enricher import NATGatewayActivityEnricher

    enricher = NATGatewayActivityEnricher(
        operational_profile='${CENTRALISED_OPS_PROFILE}',
        region='ap-southeast-2'
    )

    enriched_df = enricher.enrich_nat_gateway_activity(discovery_df)

    # Adds columns:
    # - bytes_out_90d: Sum of BytesOutToDestination over 90 days
    # - active_connections_90d: Sum of ActiveConnectionCount over 90 days
    # - packets_dropped_90d: Sum of PacketsDropCount over 90 days
    # - availability_zone: NAT Gateway availability zone
    # - vpc_environment: VPC environment tag
    # - nat_gateway_count_same_vpc: Number of NAT Gateways in same VPC
    # - unique_az_count_same_vpc: Number of unique AZs with NAT Gateways in VPC
    # - age_days: Days since NAT Gateway creation
    # - n1_signal: Zero data transfer (Boolean)
    # - n2_signal: Zero active connections (Boolean)
    # - n3_signal: Single AZ NAT Gateway (Boolean)
    # - n4_signal: Non-production VPC (Boolean)
    # - n5_signal: Age >365 days (Boolean)
    # - cloudwatch_enrichment_success: Boolean (enrichment succeeded)
    # - enrichment_status: String (SUCCESS/FAILED/PENDING)
    # - enrichment_error: String (error message if failed)
    # - decommission_score: Total score (0-100)
    # - decommission_tier: MUST/SHOULD/COULD/KEEP/UNKNOWN

Author: Runbooks Team
Version: 1.0.0
Epic: v1.1.20 FinOps Dashboard Enhancements
Track: Track 16 Phase 4 - NAT Gateway Activity Enrichment
"""

import pandas as pd
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

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

logger = logging.getLogger(__name__)

# NAT Gateway signal weights (0-100 scale)
DEFAULT_NAT_GATEWAY_WEIGHTS = {
    'N1': 40,  # Zero data transfer 90+ days (aligns with EC2 E1/S3 S1)
    'N2': 20,  # Zero active connections 90+ days
    'N3': 10,  # Single AZ NAT Gateway (not HA)
    'N4': 5,   # Non-production VPC
    'N5': 25   # Age >180 days (Manager's age emphasis for VPC)
}


class NATGatewayActivityEnricher:
    """
    NAT Gateway activity enrichment using CloudWatch metrics for N1-N5 decommission signals.

    Consolidates CloudWatch NAT Gateway metrics into actionable decommission signals:
    - BytesOutToDestination (N1: zero data transfer)
    - ActiveConnectionCount (N2: zero active connections)
    - Availability zone analysis (N3: single AZ, no HA)
    - VPC environment tags (N4: non-production)
    - Creation timestamp (N5: age >365 days)
    """

    def __init__(
        self,
        operational_profile: str,
        region: str = "ap-southeast-2",
        output_controller: Optional[OutputController] = None,
        lookback_days: int = 90
    ):
        """
        Initialize NAT Gateway activity enricher.

        Args:
            operational_profile: AWS profile for CloudWatch API access
            region: AWS region for API calls (default: ap-southeast-2)
            output_controller: OutputController for verbose output (optional)
            lookback_days: CloudWatch metrics lookback period (default: 90 days)

        Profile Requirements:
            - cloudwatch:GetMetricStatistics (NAT Gateway namespace metrics)
            - ec2:DescribeNatGateways (NAT Gateway metadata)
            - ec2:DescribeSubnets (availability zone analysis)
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

        # Cache for VPC NAT Gateway counts (avoid repeated API calls)
        self._vpc_nat_gateway_cache: Dict[str, Dict] = {}

        if self.output_controller.verbose:
            print_info(f"🔍 NATGatewayActivityEnricher initialized: profile={resolved_profile}, region={region}")
            print_info(f"   Metrics: BytesOutToDestination, ActiveConnectionCount, PacketsDropCount, AZ Analysis")
        else:
            logger.debug(f"NATGatewayActivityEnricher initialized: profile={resolved_profile}, region={region}")

    def enrich_nat_gateway_activity(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich NAT Gateway DataFrame with N1-N5 activity signals.

        Args:
            df: DataFrame with nat_gateway_id column

        Returns:
            DataFrame with NAT Gateway activity columns and decommission signals

        Columns Added:
            - bytes_out_90d: Sum of BytesOutToDestination over 90 days
            - active_connections_90d: Sum of ActiveConnectionCount over 90 days
            - packets_dropped_90d: Sum of PacketsDropCount over 90 days
            - availability_zone: NAT Gateway availability zone
            - vpc_environment: VPC environment tag
            - nat_gateway_count_same_vpc: Number of NAT Gateways in same VPC
            - unique_az_count_same_vpc: Number of unique AZs with NAT Gateways in VPC
            - age_days: Days since NAT Gateway creation
            - n1_signal: Zero data transfer (Boolean)
            - n2_signal: Zero active connections (Boolean)
            - n3_signal: Single AZ NAT Gateway (Boolean)
            - n4_signal: Non-production VPC (Boolean)
            - n5_signal: Age >365 days (Boolean)
            - cloudwatch_enrichment_success: Boolean (enrichment succeeded)
            - enrichment_status: String (SUCCESS/FAILED/PENDING)
            - enrichment_error: String (error message if failed)
            - decommission_score: Total score (0-100)
            - decommission_tier: MUST/SHOULD/COULD/KEEP/UNKNOWN
        """
        # Graceful degradation: skip enrichment if no NAT Gateways discovered
        if df.empty:
            if self.output_controller.verbose:
                print_warning("⚠️  NAT Gateway enrichment skipped - no NAT Gateways discovered")
            logger.info("NAT Gateway enrichment skipped - empty DataFrame")
            return df

        # Prerequisite validation: check for required column
        if 'nat_gateway_id' not in df.columns:
            # v1.1.20: Changed to DEBUG - graceful degradation, not an error condition
            logger.debug(
                "NAT Gateway enrichment skipped - nat_gateway_id column not found",
                extra={
                    "reason": "Missing required column",
                    "signal_impact": "N1-N5 signals unavailable",
                    "alternative": "Ensure NAT Gateway discovery completed before enrichment"
                }
            )
            return df

        if self.output_controller.verbose:
            print_info(f"🔄 Starting NAT Gateway activity enrichment for {len(df)} NAT Gateways...")
        else:
            logger.info(f"NAT Gateway activity enrichment started for {len(df)} NAT Gateways")

        # Initialize activity columns with defaults
        activity_columns = {
            'bytes_out_90d': 0,
            'active_connections_90d': 0,
            'packets_dropped_90d': 0,
            'availability_zone': 'unknown',
            'vpc_environment': 'unknown',
            'nat_gateway_count_same_vpc': 0,
            'unique_az_count_same_vpc': 0,
            'age_days': 0,
            'n1_signal': False,
            'n2_signal': False,
            'n3_signal': False,
            'n4_signal': False,
            'n5_signal': False,
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

        # Enrich each NAT Gateway with CloudWatch metrics and availability zone analysis
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=self.lookback_days)

        with create_progress_bar() as progress:
            task = progress.add_task("[cyan]CloudWatch NAT Gateway metrics...", total=len(df))

            for idx, row in df.iterrows():
                nat_gateway_id = row.get('nat_gateway_id', '')

                if not nat_gateway_id or nat_gateway_id == 'N/A':
                    progress.update(task, advance=1)
                    continue

                try:
                    # Get NAT Gateway metadata
                    nat_response = self.ec2.describe_nat_gateways(
                        NatGatewayIds=[nat_gateway_id]
                    )

                    nat_gateways = nat_response.get('NatGateways', [])
                    if not nat_gateways:
                        logger.debug(f"NAT Gateway not found: {nat_gateway_id}")
                        df.at[idx, 'enrichment_status'] = 'FAILED'
                        df.at[idx, 'enrichment_error'] = 'NAT Gateway not found'
                        progress.update(task, advance=1)
                        continue

                    nat_metadata = nat_gateways[0]
                    vpc_id = nat_metadata.get('VpcId', '')
                    subnet_id = nat_metadata.get('SubnetId', '')
                    creation_time = nat_metadata.get('CreateTime')
                    state = nat_metadata.get('State', '')

                    # V5: Age calculation
                    if creation_time:
                        age_days = (datetime.now(timezone.utc) - creation_time).days
                        df.at[idx, 'age_days'] = age_days

                    # N3: Availability zone analysis via subnet
                    if subnet_id:
                        try:
                            subnet_response = self.ec2.describe_subnets(SubnetIds=[subnet_id])
                            subnets = subnet_response.get('Subnets', [])

                            if subnets:
                                availability_zone = subnets[0].get('AvailabilityZone', 'unknown')
                                df.at[idx, 'availability_zone'] = availability_zone

                        except Exception as subnet_error:
                            logger.debug(
                                f"Subnet retrieval failed for {subnet_id}: {subnet_error}",
                                extra={
                                    "subnet_id": subnet_id,
                                    "error_type": type(subnet_error).__name__
                                }
                            )

                    # N3: Count NAT Gateways and unique AZs in same VPC
                    if vpc_id:
                        vpc_analysis = self._get_vpc_nat_gateway_analysis(vpc_id)
                        df.at[idx, 'nat_gateway_count_same_vpc'] = vpc_analysis['total_count']
                        df.at[idx, 'unique_az_count_same_vpc'] = vpc_analysis['unique_az_count']

                    # N4: VPC environment tag
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

                    # N1 & N2: CloudWatch metrics (BytesOutToDestination/ActiveConnectionCount/PacketsDropCount)
                    metrics_available = False
                    try:
                        # BytesOutToDestination metric
                        bytes_out_response = self.cloudwatch.get_metric_statistics(
                            Namespace='AWS/NATGateway',
                            MetricName='BytesOutToDestination',
                            Dimensions=[
                                {'Name': 'NatGatewayId', 'Value': nat_gateway_id}
                            ],
                            StartTime=start_time,
                            EndTime=end_time,
                            Period=86400,  # 1-day aggregation
                            Statistics=['Sum'],
                            Unit='Bytes'
                        )

                        bytes_out_datapoints = bytes_out_response.get('Datapoints', [])
                        if bytes_out_datapoints:
                            total_bytes_out = sum([dp['Sum'] for dp in bytes_out_datapoints])
                            df.at[idx, 'bytes_out_90d'] = int(total_bytes_out)
                            metrics_available = True

                        # ActiveConnectionCount metric
                        connections_response = self.cloudwatch.get_metric_statistics(
                            Namespace='AWS/NATGateway',
                            MetricName='ActiveConnectionCount',
                            Dimensions=[
                                {'Name': 'NatGatewayId', 'Value': nat_gateway_id}
                            ],
                            StartTime=start_time,
                            EndTime=end_time,
                            Period=86400,
                            Statistics=['Sum'],
                            Unit='Count'
                        )

                        connections_datapoints = connections_response.get('Datapoints', [])
                        if connections_datapoints:
                            total_connections = sum([dp['Sum'] for dp in connections_datapoints])
                            df.at[idx, 'active_connections_90d'] = int(total_connections)
                            metrics_available = True

                        # PacketsDropCount metric (optional - may not exist)
                        try:
                            packets_dropped_response = self.cloudwatch.get_metric_statistics(
                                Namespace='AWS/NATGateway',
                                MetricName='PacketsDropCount',
                                Dimensions=[
                                    {'Name': 'NatGatewayId', 'Value': nat_gateway_id}
                                ],
                                StartTime=start_time,
                                EndTime=end_time,
                                Period=86400,
                                Statistics=['Sum'],
                                Unit='Count'
                            )

                            packets_dropped_datapoints = packets_dropped_response.get('Datapoints', [])
                            if packets_dropped_datapoints:
                                total_packets_dropped = sum([dp['Sum'] for dp in packets_dropped_datapoints])
                                df.at[idx, 'packets_dropped_90d'] = int(total_packets_dropped)
                        except Exception:
                            # PacketsDropCount metric may not exist - graceful degradation
                            pass

                        if metrics_available:
                            df.at[idx, 'cloudwatch_enrichment_success'] = True
                            df.at[idx, 'enrichment_status'] = 'SUCCESS'

                    except Exception as metrics_error:
                        # Graceful degradation: CloudWatch metrics may not exist
                        logger.debug(
                            f"CloudWatch metrics unavailable for NAT Gateway {nat_gateway_id}: {metrics_error}",
                            extra={
                                "nat_gateway_id": nat_gateway_id,
                                "error_type": type(metrics_error).__name__,
                                "note": "NAT Gateway metrics availability varies by region"
                            }
                        )
                        # Continue with availability zone and VPC environment analysis

                except Exception as e:
                    logger.warning(
                        f"NAT Gateway enrichment failed for {nat_gateway_id}: {e}",
                        extra={
                            "nat_gateway_id": nat_gateway_id,
                            "error_type": type(e).__name__,
                            "lookback_days": self.lookback_days,
                            "region": self.region
                        }
                    )
                    df.at[idx, 'enrichment_status'] = 'FAILED'
                    df.at[idx, 'enrichment_error'] = str(e)

                progress.update(task, advance=1)

        # Calculate decommission signals and scores
        df = self._calculate_decommission_signals(df)

        metrics_found = (df['bytes_out_90d'] > 0).sum() + (df['active_connections_90d'] > 0).sum()
        if self.output_controller.verbose:
            print_success(f"✅ NAT Gateway enrichment complete: {metrics_found} data points collected")
        else:
            logger.info(f"NAT Gateway enrichment complete: {metrics_found} data points collected")

        return df

    def _get_vpc_nat_gateway_analysis(self, vpc_id: str) -> Dict[str, int]:
        """
        Get NAT Gateway count and unique AZ count for a VPC.

        Args:
            vpc_id: VPC ID to analyze

        Returns:
            Dict with total_count and unique_az_count
        """
        # Check cache first
        if vpc_id in self._vpc_nat_gateway_cache:
            return self._vpc_nat_gateway_cache[vpc_id]

        try:
            # Query all NAT Gateways in this VPC
            nat_response = self.ec2.describe_nat_gateways(
                Filters=[
                    {'Name': 'vpc-id', 'Values': [vpc_id]},
                    {'Name': 'state', 'Values': ['available']}
                ]
            )

            nat_gateways = nat_response.get('NatGateways', [])
            total_count = len(nat_gateways)

            # Get unique availability zones
            availability_zones = set()
            for nat_gateway in nat_gateways:
                subnet_id = nat_gateway.get('SubnetId', '')
                if subnet_id:
                    try:
                        subnet_response = self.ec2.describe_subnets(SubnetIds=[subnet_id])
                        subnets = subnet_response.get('Subnets', [])
                        if subnets:
                            az = subnets[0].get('AvailabilityZone')
                            if az:
                                availability_zones.add(az)
                    except Exception:
                        # Graceful degradation - skip subnet if unavailable
                        pass

            unique_az_count = len(availability_zones)

            result = {
                'total_count': total_count,
                'unique_az_count': unique_az_count
            }

            # Cache result
            self._vpc_nat_gateway_cache[vpc_id] = result

            return result

        except Exception as e:
            logger.debug(
                f"VPC NAT Gateway analysis failed for {vpc_id}: {e}",
                extra={
                    "vpc_id": vpc_id,
                    "error_type": type(e).__name__
                }
            )
            return {'total_count': 0, 'unique_az_count': 0}

    def _get_nat_gateway_route_analysis(self, nat_gateway_id: str) -> Dict[str, Any]:
        """
        Check if NAT Gateway has active route table entries.

        Returns:
            {
                'has_routes': bool,
                'route_count': int,
                'route_table_available': bool
            }
        """
        # Check cache first
        if not hasattr(self, '_route_cache'):
            self._route_cache = {}

        if nat_gateway_id in self._route_cache:
            return self._route_cache[nat_gateway_id]

        try:
            route_tables = self.ec2.describe_route_tables(
                Filters=[
                    {'Name': 'route.nat-gateway-id', 'Values': [nat_gateway_id]}
                ]
            )

            result = {
                'has_routes': len(route_tables['RouteTables']) > 0,
                'route_count': len(route_tables['RouteTables']),
                'route_table_available': True
            }

            # Cache result
            self._route_cache[nat_gateway_id] = result
            return result

        except Exception as e:
            logger.debug(f"Route table query failed for {nat_gateway_id}: {e}")
            return {
                'has_routes': False,
                'route_count': 0,
                'route_table_available': False
            }

    def _check_alternative_egress(self, nat_gateway_id: str, vpc_id: str) -> Dict[str, Any]:
        """
        Check if private subnets have alternative egress (IGW or other NAT).

        Simplified logic:
        1. Find route tables using this NAT Gateway
        2. Check for IGW route (0.0.0.0/0 → igw-*)
        3. Check for another NAT Gateway route

        Returns:
            {
                'has_alternative': bool,
                'alternative_type': str,  # 'igw', 'nat', 'none'
                'route_table_available': bool
            }
        """
        try:
            # Find route tables using this NAT
            route_tables = self.ec2.describe_route_tables(
                Filters=[
                    {'Name': 'route.nat-gateway-id', 'Values': [nat_gateway_id]}
                ]
            )

            if not route_tables['RouteTables']:
                return {
                    'has_alternative': False,
                    'alternative_type': 'none',
                    'route_table_available': True
                }

            # Check for IGW or other NAT in same VPC
            for rt in route_tables['RouteTables']:
                for route in rt.get('Routes', []):
                    destination = route.get('DestinationCidrBlock', '')
                    gateway_id = route.get('GatewayId', '')
                    nat_gw = route.get('NatGatewayId', '')

                    # IGW route = alternative egress
                    if destination == '0.0.0.0/0' and gateway_id.startswith('igw-'):
                        return {
                            'has_alternative': True,
                            'alternative_type': 'igw',
                            'route_table_available': True
                        }

                    # Another NAT = alternative egress
                    if nat_gw and nat_gw != nat_gateway_id:
                        return {
                            'has_alternative': True,
                            'alternative_type': 'nat',
                            'route_table_available': True
                        }

            return {
                'has_alternative': False,
                'alternative_type': 'none',
                'route_table_available': True
            }

        except Exception as e:
            logger.debug(f"Alternative egress check failed: {e}")
            return {
                'has_alternative': False,
                'alternative_type': 'none',
                'route_table_available': False
            }

    def _calculate_decommission_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate N1-N5 decommission signals and scores.

        Args:
            df: DataFrame with NAT Gateway activity columns

        Returns:
            DataFrame with signal columns and decommission scores populated
        """
        # Initialize route cache for route table queries
        self._route_cache = {}

        for idx, row in df.iterrows():
            nat_gateway_id = row.get('nat_gateway_id')
            vpc_id = row.get('vpc_id')

            # Check signal availability for dynamic denominator
            cloudwatch_success = row.get('cloudwatch_enrichment_success', False)

            # Check route table availability (used by N2A and N3A)
            route_analysis = self._get_nat_gateway_route_analysis(nat_gateway_id)
            route_table_available = route_analysis['route_table_available']

            # Calculate total possible score based on signal availability
            total_possible = self._calculate_total_possible_score(
                cloudwatch_success,
                route_table_available
            )
            df.at[idx, 'total_possible_score'] = total_possible

            signals = {}

            # N1: Zero data transfer (40 points) - No BytesOutToDestination for 90+ days
            bytes_out = row.get('bytes_out_90d', 0)

            # Note: If CloudWatch metrics unavailable, N1 cannot be determined
            # Only trigger N1 if metrics available and show zero transfer
            if cloudwatch_success and bytes_out == 0:
                df.at[idx, 'n1_signal'] = True
                signals['N1'] = DEFAULT_NAT_GATEWAY_WEIGHTS['N1']
            else:
                signals['N1'] = 0

            # N2: Hybrid signal (routes + connections) - 20 points total
            # N2A: No route table entries (10pts)
            if route_table_available and not route_analysis['has_routes']:
                df.at[idx, 'n2a_signal'] = True
                signals['N2A'] = 10
            else:
                df.at[idx, 'n2a_signal'] = False
                signals['N2A'] = 0

            # N2B: Zero CloudWatch connections (10pts - adjusted from 5pts for 20pt total)
            active_connections = row.get('active_connections_90d', 0)
            if cloudwatch_success and active_connections == 0:
                df.at[idx, 'n2b_signal'] = True
                signals['N2B'] = 10
            else:
                df.at[idx, 'n2b_signal'] = False
                signals['N2B'] = 0

            # Total N2 signal
            signals['N2'] = signals['N2A'] + signals['N2B']
            df.at[idx, 'n2_signal'] = (signals['N2'] > 0)

            # N3: Hybrid signal (egress + HA) - 10 points total
            # N3A: Alternative egress exists (5pts - adjusted for balance)
            egress_analysis = self._check_alternative_egress(nat_gateway_id, vpc_id)
            if route_table_available and not egress_analysis['has_alternative']:
                df.at[idx, 'n3a_signal'] = True
                signals['N3A'] = 5
            else:
                df.at[idx, 'n3a_signal'] = False
                signals['N3A'] = 0

            # N3B: Single AZ deployment (5pts)
            unique_az_count = row.get('unique_az_count_same_vpc', 0)
            if unique_az_count == 1:
                df.at[idx, 'n3b_signal'] = True
                signals['N3B'] = 5
            else:
                df.at[idx, 'n3b_signal'] = False
                signals['N3B'] = 0

            # Total N3 signal
            signals['N3'] = signals['N3A'] + signals['N3B']
            df.at[idx, 'n3_signal'] = (signals['N3'] > 0)

            # N4: Non-production VPC (5 points)
            vpc_environment = row.get('vpc_environment', 'unknown').lower()

            nonprod_environments = ['nonprod', 'dev', 'test', 'staging']
            if vpc_environment in nonprod_environments:
                df.at[idx, 'n4_signal'] = True
                signals['N4'] = DEFAULT_NAT_GATEWAY_WEIGHTS['N4']
            else:
                signals['N4'] = 0

            # N5: Age >180 days (25 points - Manager's adjustment)
            age_days = row.get('age_days', 0)
            if age_days > 180:
                df.at[idx, 'n5_signal'] = True
                signals['N5'] = DEFAULT_NAT_GATEWAY_WEIGHTS['N5']
            else:
                signals['N5'] = 0

            # Calculate total decommission score
            total_score = sum(signals.values())
            df.at[idx, 'decommission_score'] = total_score

            # Determine decommission tier with dynamic threshold adjustment
            tier = self._calculate_tier_with_dynamic_scoring(total_score, total_possible)
            df.at[idx, 'decommission_tier'] = tier

        return df

    def _calculate_total_possible_score(
        self,
        cloudwatch_enrichment_success: bool,
        route_table_available: bool
    ) -> int:
        """
        Calculate NAT Gateway total possible score with dynamic denominator.

        Implements manager's pattern: Adjust denominator when APIs unavailable.

        Args:
            cloudwatch_enrichment_success: Whether CloudWatch metrics succeeded
            route_table_available: Whether EC2 route table API succeeded

        Returns:
            Total possible score (30-100 range)
        """
        base_score = 100

        # N1 depends on CloudWatch (40pts)
        if not cloudwatch_enrichment_success:
            base_score -= DEFAULT_NAT_GATEWAY_WEIGHTS['N1']  # -40

        # N2B depends on CloudWatch (10pts)
        if not cloudwatch_enrichment_success:
            base_score -= 10

        # N2A + N3A depend on route table API (10pts + 5pts = 15pts)
        if not route_table_available:
            base_score -= 15

        # Possible scores: 100 (all available), 50 (no CloudWatch),
        # 85 (no routes), 35 (neither), minimum 30 (N3B+N4+N5)
        return base_score

    def _calculate_tier_with_dynamic_scoring(self, score: int, total_possible: int) -> str:
        """
        Calculate tier with dynamic threshold adjustment.

        Implements manager's proportional tier adjustment:
        - Full signals (100): MUST=80, SHOULD=50, COULD=25
        - Reduced signals: Proportional thresholds

        Args:
            score: Actual decommission score (0-100)
            total_possible: Total possible score (30-100 depending on signal availability)

        Returns:
            Tier classification (MUST/SHOULD/COULD/KEEP)
        """
        base_thresholds = {
            'MUST': 80,
            'SHOULD': 50,
            'COULD': 25,
            'KEEP': 0
        }

        if total_possible < 100:
            # Proportional adjustment: threshold * (total_possible / 100)
            adjusted_thresholds = {
                tier: int(threshold * total_possible / 100)
                for tier, threshold in base_thresholds.items()
            }
        else:
            adjusted_thresholds = base_thresholds

        # Tier classification with adjusted thresholds
        if score >= adjusted_thresholds['MUST']:
            return 'MUST'
        elif score >= adjusted_thresholds['SHOULD']:
            return 'SHOULD'
        elif score >= adjusted_thresholds['COULD']:
            return 'COULD'
        else:
            return 'KEEP'


# Export interface
__all__ = ["NATGatewayActivityEnricher"]

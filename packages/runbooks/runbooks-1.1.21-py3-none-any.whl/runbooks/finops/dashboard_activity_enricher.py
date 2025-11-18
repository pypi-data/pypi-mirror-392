#!/usr/bin/env python3
"""
Dashboard Activity Enricher - Orchestrate Activity Signals for FinOps Dashboard

Consolidates activity enrichment from multiple proven patterns:
- EC2: ActivityEnricher (CloudTrail, CloudWatch, SSM, Compute Optimizer)
- RDS: RDSActivityEnricher (R1-R7 database activity signals)
- S3: S3LifecycleOptimizer (S1-S7 storage optimization signals - if available)

Pattern: Reuse existing enrichers, don't recreate (KISS/DRY/LEAN)

Strategic Alignment:
- Objective 1 (runbooks package): Reusable orchestration pattern
- Enterprise SDLC: Composition over duplication
- KISS/DRY/LEAN: Orchestrate existing enrichers, zero redundant code

Architecture:
- Layer 4 Activity Enrichment consolidation
- Delegates to specialized enrichers (EC2, RDS, S3)
- Lazy initialization for performance optimization
- OutputController integration for UX consistency

Usage:
    from runbooks.finops.dashboard_activity_enricher import DashboardActivityEnricher

    enricher = DashboardActivityEnricher(
        operational_profile='CENTRALISED_OPS_PROFILE',
        region='ap-southeast-2'
    )

    # Orchestrate activity enrichment for all resource types
    activity_data = enricher.enrich_all_resources(discovery_results)

    Returns:
        {
            'ec2': DataFrame with 11 activity columns (E1-E7 signals),
            'rds': DataFrame with R1-R7 database activity metrics,
            's3': DataFrame with S1-S7 storage optimization signals
        }

Example Integration:
    # Dashboard workflow integration
    discovery_results = {
        'ec2': pd.DataFrame({'instance_id': ['i-abc123', 'i-def456']}),
        'rds': pd.DataFrame({'db_instance_id': ['mydb-1', 'mydb-2']}),
        's3': pd.DataFrame({'bucket_name': ['my-bucket-1']})
    }

    # Orchestrate all activity enrichment
    enricher = DashboardActivityEnricher(operational_profile='ops-profile')
    enriched = enricher.enrich_all_resources(discovery_results)

    # Results available for dashboard consumption
    ec2_with_activity = enriched['ec2']  # 11 activity columns added
    rds_with_activity = enriched['rds']  # R1-R7 signals added

Author: Runbooks Team
Version: 1.0.0
Epic: v1.1.20 FinOps Dashboard Enhancements
Track: Track 1 - Activity Orchestration
"""

import logging
import time
from typing import Dict, List, Optional

import pandas as pd

# Reuse existing enrichers (KISS/DRY/LEAN - don't recreate functionality)
from runbooks.inventory.enrichers.activity_enricher import ActivityEnricher
from runbooks.inventory.enrichers.rds_activity import RDSActivityEnricher
from runbooks.finops.dynamodb_activity_enricher import DynamoDBActivityEnricher
from runbooks.finops.asg_activity_enricher import ASGActivityEnricher
from runbooks.inventory.enrichers.alb_activity_enricher import ALBActivityEnricher
from runbooks.inventory.enrichers.dx_activity_enricher import DXActivityEnricher
from runbooks.inventory.enrichers.route53_activity_enricher import Route53ActivityEnricher
from runbooks.inventory.enrichers.vpce_activity_enricher import VPCEActivityEnricher
from runbooks.inventory.enrichers.vpc_peering_activity_enricher import VPCPeeringActivityEnricher
from runbooks.inventory.enrichers.transit_gateway_activity_enricher import TransitGatewayActivityEnricher
from runbooks.inventory.enrichers.nat_gateway_activity_enricher import NATGatewayActivityEnricher
from runbooks.finops.base_enrichers import StorageIOEnricher  # E6 Storage I/O signal

# Import S3 analyzer if available (graceful degradation)
try:
    from runbooks.finops.s3_lifecycle_optimizer import S3LifecycleOptimizer
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False
    logging.warning("S3LifecycleOptimizer not available - S3 enrichment disabled")

# Rich CLI integration for consistent UX
from runbooks.common.rich_utils import (
    print_info, print_success, print_warning, print_error,
    create_progress_bar, console
)
from runbooks.common.profile_utils import (
    get_profile_for_operation,
    create_operational_session
)
from runbooks.common.output_controller import OutputController

logger = logging.getLogger(__name__)


class DashboardActivityEnricher:
    """
    Orchestrate activity enrichment for FinOps dashboard using existing enrichers.

    Consolidates proven patterns from inventory module with zero code duplication:
    - EC2: 11 activity columns (CloudTrail, CloudWatch, SSM, Compute Optimizer)
    - RDS: R1-R7 database activity signals with confidence scoring
    - DynamoDB: D1-D5 NoSQL database activity signals
    - S3: S1-S7 storage optimization signals (if available)

    Architecture Pattern:
    - Composition over inheritance (delegates to specialized enrichers)
    - Lazy initialization (performance optimization)
    - Graceful degradation (handles missing S3 enricher)
    - OutputController integration (verbose flag support)

    KISS/DRY/LEAN Compliance:
    - Reuses ActivityEnricher (inventory/enrichers/activity_enricher.py)
    - Reuses RDSActivityEnricher (inventory/enrichers/rds_activity.py)
    - Zero redundant AWS API code
    - Single orchestration responsibility

    Example:
        >>> enricher = DashboardActivityEnricher(
        ...     operational_profile='ops-profile',
        ...     region='ap-southeast-2'
        ... )
        >>>
        >>> discovery = {
        ...     'ec2': pd.DataFrame({'instance_id': ['i-abc123']}),
        ...     'rds': pd.DataFrame({'db_instance_id': ['mydb-1']})
        ... }
        >>>
        >>> enriched = enricher.enrich_all_resources(discovery)
        >>> print(enriched['ec2'].columns)  # Shows 11 activity columns added
    """

    def __init__(
        self,
        operational_profile: str,
        region: str = "ap-southeast-2",
        output_controller: Optional[OutputController] = None,
        lookback_days: int = 90
    ):
        """
        Initialize dashboard activity enricher with lazy-loaded delegated enrichers.

        Args:
            operational_profile: AWS profile for operational APIs (CloudTrail, CloudWatch, SSM, etc.)
            region: AWS region for API calls (default: ap-southeast-2)
            output_controller: OutputController for verbose flag handling (creates new if None)
            lookback_days: CloudWatch metrics lookback period (default: 90 days)

        Profile Requirements:
            - CloudTrail: cloudtrail:LookupEvents (EC2 activity tracking)
            - CloudWatch: cloudwatch:GetMetricStatistics (metrics collection)
            - SSM: ssm:DescribeInstanceInformation (EC2 agent status)
            - Compute Optimizer: compute-optimizer:GetEC2InstanceRecommendations (idle detection)
            - RDS: rds:DescribeDBInstances + cloudwatch:GetMetricStatistics (database activity)

        Design Pattern:
            Lazy initialization via @property pattern prevents blocking startup time.
            Enrichers only initialized when actually used (performance optimization).
        """
        self.profile = operational_profile
        self.region = region
        self.output_controller = output_controller or OutputController()
        self.lookback_days = lookback_days

        # Initialize reusable enrichers (lazy loading for performance)
        self._ec2_enricher = None
        self._rds_enricher = None
        self._dynamodb_enricher = None
        self._asg_enricher = None
        self._alb_enricher = None
        self._dx_enricher = None
        self._route53_enricher = None
        self._vpce_enricher = None
        self._vpc_peering_enricher = None
        self._transit_gateway_enricher = None
        self._nat_gateway_enricher = None
        self._s3_analyzer = None

        # Performance tracking
        self._enrichment_stats = {
            'ec2_count': 0,
            'rds_count': 0,
            'dynamodb_count': 0,
            'asg_count': 0,
            'alb_count': 0,
            'nlb_count': 0,
            'dx_count': 0,
            'route53_count': 0,
            's3_count': 0,
            'total_time': 0.0
        }

        if self.output_controller.verbose:
            print_info(f"🎯 DashboardActivityEnricher initialized")
            print_info(f"   Profile: {operational_profile}")
            print_info(f"   Region: {region}")
            print_info(f"   Lookback: {lookback_days} days")
            print_info(f"   Enrichers: EC2 (lazy), RDS (lazy), DynamoDB (lazy), ASG (lazy), ALB (lazy), DX (lazy), Route53 (lazy), S3 ({'available' if S3_AVAILABLE else 'disabled'})")

    @property
    def ec2_enricher(self) -> ActivityEnricher:
        """
        Lazy initialize EC2 activity enricher.

        Returns:
            ActivityEnricher instance from inventory/enrichers/activity_enricher.py

        Design:
            Lazy initialization prevents blocking startup when EC2 enrichment not needed.
            Enricher initialized only on first access (performance optimization).
        """
        if self._ec2_enricher is None:
            if self.output_controller.verbose:
                print_info("   Initializing EC2 ActivityEnricher (CloudTrail + CloudWatch + SSM + Compute Optimizer)...")

            self._ec2_enricher = ActivityEnricher(
                operational_profile=self.profile,
                region=self.region,
                output_controller=self.output_controller
            )

            if self.output_controller.verbose:
                print_success("   ✅ EC2 ActivityEnricher ready")

        return self._ec2_enricher

    @property
    def rds_enricher(self) -> RDSActivityEnricher:
        """
        Lazy initialize RDS activity enricher.

        Returns:
            RDSActivityEnricher instance from inventory/enrichers/rds_activity.py

        Design:
            Lazy initialization prevents blocking startup when RDS enrichment not needed.
            Enricher initialized only on first access (performance optimization).
        """
        if self._rds_enricher is None:
            if self.output_controller.verbose:
                print_info("   Initializing RDS ActivityEnricher (R1-R7 signals)...")

            self._rds_enricher = RDSActivityEnricher(
                operational_profile=self.profile,
                region=self.region,
                lookback_days=self.lookback_days,
                enable_mcp_validation=False  # Disabled by default for performance
            )

            if self.output_controller.verbose:
                print_success("   ✅ RDS ActivityEnricher ready")

        return self._rds_enricher

    @property
    def asg_enricher(self) -> ASGActivityEnricher:
        """
        Lazy initialize ASG activity enricher.

        Returns:
            ASGActivityEnricher instance from finops/asg_activity_enricher.py

        Design:
            Lazy initialization prevents blocking startup when ASG enrichment not needed.
            Enricher initialized only on first access (performance optimization).
        """
        if self._asg_enricher is None:
            if self.output_controller.verbose:
                print_info("   Initializing ASG ActivityEnricher (A1-A5 signals)...")

            self._asg_enricher = ASGActivityEnricher(
                operational_profile=self.profile,
                region=self.region,
                output_controller=self.output_controller
            )

            if self.output_controller.verbose:
                print_success("   ✅ ASG ActivityEnricher ready")

        return self._asg_enricher

    @property
    def alb_enricher(self) -> ALBActivityEnricher:
        """
        Lazy initialize ALB activity enricher.

        Returns:
            ALBActivityEnricher instance from inventory/enrichers/alb_activity_enricher.py

        Design:
            Lazy initialization prevents blocking startup when ALB enrichment not needed.
            Enricher initialized only on first access (performance optimization).
        """
        if self._alb_enricher is None:
            if self.output_controller.verbose:
                print_info("   Initializing ALB ActivityEnricher (L1-L5 signals)...")

            self._alb_enricher = ALBActivityEnricher(
                operational_profile=self.profile,
                region=self.region,
                output_controller=self.output_controller,
                lookback_days=self.lookback_days
            )

            if self.output_controller.verbose:
                print_success("   ✅ ALB ActivityEnricher ready")

        return self._alb_enricher

    @property
    def s3_analyzer(self):
        """
        Lazy initialize S3 lifecycle optimizer/analyzer.

        Returns:
            S3LifecycleOptimizer instance from finops/s3_lifecycle_optimizer.py

        Design:
            Lazy initialization prevents blocking startup when S3 enrichment not needed.
            Analyzer initialized only on first access (performance optimization).
        """
        if self._s3_analyzer is None and S3_AVAILABLE:
            if self.output_controller.verbose:
                print_info("   Initializing S3LifecycleOptimizer (S1-S7 signals)...")

            from runbooks.finops.s3_lifecycle_optimizer import S3LifecycleOptimizer

            self._s3_analyzer = S3LifecycleOptimizer(
                profile_name=self.profile,
                regions=[self.region]
            )

            if self.output_controller.verbose:
                print_success("   ✅ S3LifecycleOptimizer ready")

        return self._s3_analyzer

    @property
    def dynamodb_enricher(self) -> DynamoDBActivityEnricher:
        """
        Lazy initialize DynamoDB activity enricher.

        Returns:
            DynamoDBActivityEnricher instance from finops/dynamodb_activity_enricher.py

        Design:
            Lazy initialization prevents blocking startup when DynamoDB enrichment not needed.
            Enricher initialized only on first access (performance optimization).
        """
        if self._dynamodb_enricher is None:
            if self.output_controller.verbose:
                print_info("   Initializing DynamoDB ActivityEnricher (D1-D5 signals)...")

            self._dynamodb_enricher = DynamoDBActivityEnricher(
                operational_profile=self.profile,
                region=self.region,
                lookback_days=self.lookback_days,
                output_controller=self.output_controller
            )

            if self.output_controller.verbose:
                print_success("   ✅ DynamoDB ActivityEnricher ready")

        return self._dynamodb_enricher

    @property
    def dx_enricher(self) -> DXActivityEnricher:
        """
        Lazy initialize Direct Connect activity enricher.

        Returns:
            DXActivityEnricher instance from inventory/enrichers/dx_activity_enricher.py

        Design:
            Lazy initialization prevents blocking startup when DX enrichment not needed.
            Enricher initialized only on first access (performance optimization).
        """
        if self._dx_enricher is None:
            if self.output_controller.verbose:
                print_info("   Initializing DX ActivityEnricher (DX1-DX4 signals)...")

            self._dx_enricher = DXActivityEnricher(
                operational_profile=self.profile,
                region=self.region,
                output_controller=self.output_controller,
                lookback_days=self.lookback_days
            )

            if self.output_controller.verbose:
                print_success("   ✅ DX ActivityEnricher ready")

        return self._dx_enricher

    @property
    def route53_enricher(self) -> Route53ActivityEnricher:
        """
        Lazy initialize Route53 activity enricher.

        Returns:
            Route53ActivityEnricher instance from inventory/enrichers/route53_activity_enricher.py

        Design:
            Lazy initialization prevents blocking startup when Route53 enrichment not needed.
            Enricher initialized only on first access (performance optimization).
        """
        if self._route53_enricher is None:
            if self.output_controller.verbose:
                print_info("   Initializing Route53 ActivityEnricher (R53-1 to R53-4 signals)...")

            self._route53_enricher = Route53ActivityEnricher(
                operational_profile=self.profile,
                region=self.region,
                output_controller=self.output_controller,
                lookback_days=self.lookback_days
            )

            if self.output_controller.verbose:
                print_success("   ✅ Route53 ActivityEnricher ready")

        return self._route53_enricher

    @property
    def vpce_enricher(self) -> VPCEActivityEnricher:
        """
        Lazy initialize VPC Endpoint activity enricher.

        Returns:
            VPCEActivityEnricher instance from inventory/enrichers/vpce_activity_enricher.py

        Design:
            Lazy initialization prevents blocking startup when VPCE enrichment not needed.
            Enricher initialized only on first access (performance optimization).
        """
        if self._vpce_enricher is None:
            if self.output_controller.verbose:
                print_info("   Initializing VPCE ActivityEnricher (V1-V5 signals)...")

            self._vpce_enricher = VPCEActivityEnricher(
                operational_profile=self.profile,
                region=self.region,
                output_controller=self.output_controller,
                lookback_days=self.lookback_days
            )

            if self.output_controller.verbose:
                print_success("   ✅ VPCE ActivityEnricher ready")

        return self._vpce_enricher

    @property
    def vpc_peering_enricher(self) -> VPCPeeringActivityEnricher:
        """
        Lazy initialize VPC Peering activity enricher.

        Returns:
            VPCPeeringActivityEnricher instance from inventory/enrichers/vpc_peering_activity_enricher.py

        Design:
            Lazy initialization prevents blocking startup when VPC Peering enrichment not needed.
            Enricher initialized only on first access (performance optimization).
        """
        if self._vpc_peering_enricher is None:
            if self.output_controller.verbose:
                print_info("   Initializing VPC Peering ActivityEnricher (V1-V5 signals)...")

            self._vpc_peering_enricher = VPCPeeringActivityEnricher(
                operational_profile=self.profile,
                region=self.region,
                output_controller=self.output_controller,
                lookback_days=self.lookback_days
            )

            if self.output_controller.verbose:
                print_success("   ✅ VPC Peering ActivityEnricher ready")

        return self._vpc_peering_enricher

    @property
    def transit_gateway_enricher(self) -> TransitGatewayActivityEnricher:
        """
        Lazy initialize Transit Gateway activity enricher.

        Returns:
            TransitGatewayActivityEnricher instance from inventory/enrichers/transit_gateway_activity_enricher.py

        Design:
            Lazy initialization prevents blocking startup when Transit Gateway enrichment not needed.
            Enricher initialized only on first access (performance optimization).
        """
        if self._transit_gateway_enricher is None:
            if self.output_controller.verbose:
                print_info("   Initializing Transit Gateway ActivityEnricher (V1-V5 signals)...")

            self._transit_gateway_enricher = TransitGatewayActivityEnricher(
                operational_profile=self.profile,
                region=self.region,
                output_controller=self.output_controller,
                lookback_days=self.lookback_days
            )

            if self.output_controller.verbose:
                print_success("   ✅ Transit Gateway ActivityEnricher ready")

        return self._transit_gateway_enricher

    @property
    def nat_gateway_enricher(self) -> NATGatewayActivityEnricher:
        """
        Lazy initialize NAT Gateway activity enricher.

        Returns:
            NATGatewayActivityEnricher instance from inventory/enrichers/nat_gateway_activity_enricher.py

        Design:
            Lazy initialization prevents blocking startup when NAT Gateway enrichment not needed.
            Enricher initialized only on first access (performance optimization).
        """
        if self._nat_gateway_enricher is None:
            if self.output_controller.verbose:
                print_info("   Initializing NAT Gateway ActivityEnricher (N1-N5 signals)...")

            self._nat_gateway_enricher = NATGatewayActivityEnricher(
                operational_profile=self.profile,
                region=self.region,
                output_controller=self.output_controller,
                lookback_days=self.lookback_days
            )

            if self.output_controller.verbose:
                print_success("   ✅ NAT Gateway ActivityEnricher ready")

        return self._nat_gateway_enricher

    def enrich_ec2_activity(self, ec2_instances: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich EC2 instances with activity signals.

        Delegates to ActivityEnricher (inventory/enrichers/activity_enricher.py) for:
        - CloudTrail: last_activity_date, days_since_activity, activity_count_90d
        - CloudWatch: p95_cpu_utilization, p95_network_bytes, user_connected_sum
        - SSM: ssm_ping_status, ssm_last_ping_date, ssm_days_since_ping
        - Compute Optimizer: compute_optimizer_finding, compute_optimizer_cpu_max, compute_optimizer_recommendation

        Args:
            ec2_instances: DataFrame with instance_id column (from discovery)

        Returns:
            Enhanced DataFrame with 11 activity columns (E1-E7 decommission signals)

        Performance:
            - Graceful degradation on empty input
            - Progress tracking via OutputController verbose flag
            - Multi-API consolidation (4 AWS services)

        Example:
            >>> df = pd.DataFrame({'instance_id': ['i-abc123', 'i-def456']})
            >>> enriched = enricher.enrich_ec2_activity(df)
            >>> print(enriched.columns)
            # Shows: instance_id, last_activity_date, days_since_activity, ...
        """
        if ec2_instances.empty:
            if self.output_controller.verbose:
                print_warning("⚠️  No EC2 instances to enrich")
            return ec2_instances

        start_time = time.time()

        if self.output_controller.verbose:
            print_info(f"🔍 Enriching {len(ec2_instances)} EC2 instances with activity signals...")

        # Delegate to existing ActivityEnricher (KISS/DRY/LEAN - reuse proven code)
        enriched = self.ec2_enricher.enrich_activity(ec2_instances, resource_type='ec2')

        # E6: Storage I/O enrichment (CloudWatch DiskReadOps + DiskWriteOps metrics)
        if not enriched.empty:
            if self.output_controller.verbose:
                print_info("   💾 Enriching with Storage I/O metrics (E6 signal)...")

            storage_enricher = StorageIOEnricher()
            enriched = storage_enricher.enrich_with_storage_io(
                df=enriched,
                instance_id_column='instance_id',
                operational_profile=self.profile,
                region=self.region,
                lookback_days=14
            )

            if self.output_controller.verbose:
                idle_count = len(enriched[enriched.get('disk_total_ops_p95', 999) <= 10]) if 'disk_total_ops_p95' in enriched.columns else 0
                print_success(f"   ✅ Storage I/O enrichment complete: {idle_count} idle instances detected")

        # Update stats
        self._enrichment_stats['ec2_count'] = len(enriched)
        elapsed = time.time() - start_time
        self._enrichment_stats['total_time'] += elapsed

        if self.output_controller.verbose:
            print_success(f"✅ EC2 activity enrichment complete: {len(enriched)} instances, {elapsed:.2f}s")

        return enriched

    def enrich_rds_activity(self, rds_instances: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich RDS instances with R1-R7 activity signals.

        Delegates to RDSActivityEnricher (inventory/enrichers/rds_activity.py) for:
        - R1: Zero connections 90+ days (HIGH confidence: 0.95)
        - R2: Low connections <5/day (HIGH confidence: 0.90)
        - R3: Low CPU <5% avg 60d (MEDIUM confidence: 0.75)
        - R4: Low IOPS <100/day (MEDIUM confidence: 0.70)
        - R5: Backup-only connections (MEDIUM confidence: 0.65)
        - R6: Non-business hours only (LOW confidence: 0.50)
        - R7: Storage underutilized <20% (LOW confidence: 0.45)

        Args:
            rds_instances: DataFrame with db_instance_id column (from discovery)

        Returns:
            Enhanced DataFrame with RDS activity metrics and R1-R7 signals

        Performance:
            - Graceful degradation on empty input
            - CloudWatch metrics collection (30/60/90-day windows)
            - Confidence scoring for decommission recommendations

        Example:
            >>> df = pd.DataFrame({'db_instance_id': ['mydb-1', 'mydb-2']})
            >>> enriched = enricher.enrich_rds_activity(df)
            >>> print(enriched.columns)
            # Shows: db_instance_id, avg_connections_90d, idle_signals, ...
        """
        if rds_instances.empty:
            if self.output_controller.verbose:
                print_warning("⚠️  No RDS instances to enrich")
            return rds_instances

        start_time = time.time()

        if self.output_controller.verbose:
            print_info(f"🔍 Enriching {len(rds_instances)} RDS instances with R1-R7 activity signals...")

        # Extract instance IDs for enricher API
        instance_ids = rds_instances['db_instance_id'].tolist()

        # Delegate to existing RDSActivityEnricher (KISS/DRY/LEAN)
        analyses = self.rds_enricher.analyze_instance_activity(
            instance_ids=instance_ids,
            region=self.region,
            lookback_days=self.lookback_days
        )

        # Convert RDSActivityAnalysis objects to DataFrame columns
        enriched = self._merge_rds_analyses(rds_instances, analyses)

        # Update stats
        self._enrichment_stats['rds_count'] = len(enriched)
        elapsed = time.time() - start_time
        self._enrichment_stats['total_time'] += elapsed

        if self.output_controller.verbose:
            print_success(f"✅ RDS activity enrichment complete: {len(enriched)} instances, {elapsed:.2f}s")

        return enriched

    def _merge_rds_analyses(
        self,
        rds_instances: pd.DataFrame,
        analyses: List
    ) -> pd.DataFrame:
        """
        Merge RDSActivityAnalysis objects into DataFrame columns.

        Converts structured analysis objects into DataFrame columns for dashboard consumption.

        Args:
            rds_instances: Original RDS instances DataFrame
            analyses: List of RDSActivityAnalysis objects from enricher

        Returns:
            DataFrame with RDS activity columns merged

        Columns Added:
            - avg_connections_90d: Average connections per day (90-day window)
            - avg_cpu_percent_60d: Average CPU utilization (60-day window)
            - activity_pattern: Classified pattern (active/moderate/light/idle/backup_only)
            - idle_signals: Comma-separated R1-R7 signals
            - recommendation: Decommission recommendation (DECOMMISSION/INVESTIGATE/DOWNSIZE/KEEP)
            - confidence: Idle confidence score (0.0-1.0)
            - potential_savings: Annual savings estimate
        """
        # Create enrichment columns dictionary
        enrichment_data = {
            'avg_connections_90d': [],
            'avg_cpu_percent_60d': [],
            'avg_iops_60d': [],
            'activity_pattern': [],
            'idle_signals': [],
            'recommendation': [],
            'confidence': [],
            'monthly_cost': [],
            'potential_savings': []
        }

        # Build lookup dictionary for fast access
        analysis_lookup = {a.instance_id: a for a in analyses}

        # Populate enrichment data
        for db_instance_id in rds_instances['db_instance_id']:
            analysis = analysis_lookup.get(db_instance_id)

            if analysis:
                enrichment_data['avg_connections_90d'].append(analysis.metrics.avg_connections_90d)
                enrichment_data['avg_cpu_percent_60d'].append(analysis.metrics.avg_cpu_percent_60d)
                enrichment_data['avg_iops_60d'].append(analysis.metrics.avg_iops_60d)
                enrichment_data['activity_pattern'].append(analysis.activity_pattern.value)
                enrichment_data['idle_signals'].append(','.join([s.value for s in analysis.idle_signals]))
                enrichment_data['recommendation'].append(analysis.recommendation.value)
                enrichment_data['confidence'].append(analysis.confidence)
                enrichment_data['monthly_cost'].append(analysis.monthly_cost)
                enrichment_data['potential_savings'].append(analysis.potential_savings)
            else:
                # Default values for instances without analysis
                enrichment_data['avg_connections_90d'].append(0.0)
                enrichment_data['avg_cpu_percent_60d'].append(0.0)
                enrichment_data['avg_iops_60d'].append(0.0)
                enrichment_data['activity_pattern'].append('unknown')
                enrichment_data['idle_signals'].append('')
                enrichment_data['recommendation'].append('KEEP')
                enrichment_data['confidence'].append(0.0)
                enrichment_data['monthly_cost'].append(0.0)
                enrichment_data['potential_savings'].append(0.0)

        # Merge enrichment columns into original DataFrame
        enriched = rds_instances.copy()
        for col, values in enrichment_data.items():
            enriched[col] = values

        return enriched

    def enrich_dynamodb_activity(self, dynamodb_tables: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich DynamoDB tables with D1-D5 activity signals.

        Delegates to DynamoDBActivityEnricher (finops/dynamodb_activity_enricher.py) for:
        - D1: Low capacity utilization <5% (HIGH confidence: 0.90)
        - D2: Idle GSIs (MEDIUM confidence: 0.75)
        - D3: No PITR enabled (MEDIUM confidence: 0.60)
        - D4: No Streams activity (LOW confidence: 0.50)
        - D5: Low cost efficiency (MEDIUM confidence: 0.70)

        Args:
            dynamodb_tables: DataFrame with table_name column (from discovery)

        Returns:
            Enhanced DataFrame with DynamoDB activity metrics and D1-D5 signals

        Performance:
            - Graceful degradation on empty input
            - CloudWatch metrics collection (30/60-day windows)
            - Confidence scoring for decommission recommendations

        Example:
            >>> df = pd.DataFrame({'table_name': ['table-1', 'table-2']})
            >>> enriched = enricher.enrich_dynamodb_activity(df)
            >>> print(enriched.columns)
            # Shows: table_name, read_utilization_pct, idle_signals, ...
        """
        if dynamodb_tables.empty:
            if self.output_controller.verbose:
                print_warning("⚠️  No DynamoDB tables to enrich")
            return dynamodb_tables

        start_time = time.time()

        if self.output_controller.verbose:
            print_info(f"🔍 Enriching {len(dynamodb_tables)} DynamoDB tables with D1-D5 activity signals...")

        # Extract table names for enricher API
        table_names = dynamodb_tables['table_name'].tolist()

        # Delegate to existing DynamoDBActivityEnricher (KISS/DRY/LEAN)
        analyses = self.dynamodb_enricher.analyze_table_activity(
            table_names=table_names,
            region=self.region,
            lookback_days=self.lookback_days
        )

        # Convert DynamoDBActivityAnalysis objects to DataFrame columns
        enriched = self._merge_dynamodb_analyses(dynamodb_tables, analyses)

        # Update stats
        self._enrichment_stats['dynamodb_count'] = len(enriched)
        elapsed = time.time() - start_time
        self._enrichment_stats['total_time'] += elapsed

        if self.output_controller.verbose:
            print_success(f"✅ DynamoDB activity enrichment complete: {len(enriched)} tables, {elapsed:.2f}s")

        return enriched

    def _merge_dynamodb_analyses(
        self,
        dynamodb_tables: pd.DataFrame,
        analyses: List
    ) -> pd.DataFrame:
        """
        Merge DynamoDBActivityAnalysis objects into DataFrame columns.

        Converts structured analysis objects into DataFrame columns for dashboard consumption.

        Args:
            dynamodb_tables: Original DynamoDB tables DataFrame
            analyses: List of DynamoDBActivityAnalysis objects from enricher

        Returns:
            DataFrame with DynamoDB activity columns merged

        Columns Added:
            - read_utilization_pct: Read capacity utilization percentage
            - write_utilization_pct: Write capacity utilization percentage
            - activity_pattern: Classified pattern (active/moderate/light/idle)
            - idle_signals: Comma-separated D1-D5 signals
            - recommendation: Decommission recommendation (DECOMMISSION/INVESTIGATE/OPTIMIZE/KEEP)
            - confidence: Idle confidence score (0.0-1.0)
            - potential_savings: Annual savings estimate
        """
        # Create enrichment columns dictionary
        enrichment_data = {
            'read_utilization_pct': [],
            'write_utilization_pct': [],
            'gsi_count': [],
            'gsi_idle_count': [],
            'pitr_enabled': [],
            'streams_enabled': [],
            'activity_pattern': [],
            'idle_signals': [],
            'recommendation': [],
            'confidence': [],
            'monthly_cost': [],
            'potential_savings': [],
            'decommission_score': [],
            'decommission_tier': []
        }

        # Build lookup dictionary for fast access
        analysis_lookup = {a.table_name: a for a in analyses}

        # Populate enrichment data
        for table_name in dynamodb_tables['table_name']:
            analysis = analysis_lookup.get(table_name)

            if analysis:
                enrichment_data['read_utilization_pct'].append(analysis.metrics.read_utilization_pct)
                enrichment_data['write_utilization_pct'].append(analysis.metrics.write_utilization_pct)
                enrichment_data['gsi_count'].append(analysis.metrics.gsi_count)
                enrichment_data['gsi_idle_count'].append(analysis.metrics.gsi_idle_count)
                enrichment_data['pitr_enabled'].append(analysis.metrics.pitr_enabled)
                enrichment_data['streams_enabled'].append(analysis.metrics.streams_enabled)
                enrichment_data['activity_pattern'].append(analysis.activity_pattern.value)
                enrichment_data['idle_signals'].append(','.join([s.value for s in analysis.idle_signals]))
                enrichment_data['recommendation'].append(analysis.recommendation.value)
                enrichment_data['confidence'].append(analysis.confidence)
                enrichment_data['monthly_cost'].append(analysis.monthly_cost)
                enrichment_data['potential_savings'].append(analysis.potential_savings)
                enrichment_data['decommission_score'].append(analysis.decommission_score)
                enrichment_data['decommission_tier'].append(analysis.decommission_tier)
            else:
                # Default values for tables without analysis
                enrichment_data['read_utilization_pct'].append(0.0)
                enrichment_data['write_utilization_pct'].append(0.0)
                enrichment_data['gsi_count'].append(0)
                enrichment_data['gsi_idle_count'].append(0)
                enrichment_data['pitr_enabled'].append(False)
                enrichment_data['streams_enabled'].append(False)
                enrichment_data['activity_pattern'].append('unknown')
                enrichment_data['idle_signals'].append('')
                enrichment_data['recommendation'].append('KEEP')
                enrichment_data['confidence'].append(0.0)
                enrichment_data['monthly_cost'].append(0.0)
                enrichment_data['potential_savings'].append(0.0)
                enrichment_data['decommission_score'].append(0)
                enrichment_data['decommission_tier'].append('KEEP')

        # Merge enrichment columns into original DataFrame
        enriched = dynamodb_tables.copy()
        for col, values in enrichment_data.items():
            enriched[col] = values

        return enriched

    def enrich_asg_activity(self, asg_groups: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich Auto Scaling Groups with A1-A5 activity signals.

        Delegates to ASGActivityEnricher (finops/asg_activity_enricher.py) for:
        - A1: Scaling activity frequency (CloudWatch DesiredCapacity change events over 90 days)
        - A2: Instance health status (InService vs Desired - detect unhealthy ASGs)
        - A3: Desired vs Actual capacity delta (persistent mismatches >30 days)
        - A4: Launch configuration age (detect outdated configs - security/cost risk)
        - A5: Cost efficiency (Cost Explorer EC2 Auto Scaling filter + per-instance attribution)

        Args:
            asg_groups: DataFrame with asg_name column (from discovery)

        Returns:
            Enhanced DataFrame with 9 activity columns (A1-A5 decommission signals)

        Performance:
            - Graceful degradation on empty input
            - Progress tracking via OutputController verbose flag
            - Multi-API consolidation (Auto Scaling + CloudWatch + Cost Explorer)

        Example:
            >>> df = pd.DataFrame({'asg_name': ['my-asg-1', 'my-asg-2']})
            >>> enriched = enricher.enrich_asg_activity(df)
            >>> print(enriched.columns)
            # Shows: asg_name, scaling_activity_count_90d, a1_signal, ...
        """
        if asg_groups.empty:
            if self.output_controller.verbose:
                print_warning("⚠️  No Auto Scaling Groups to enrich")
            return asg_groups

        start_time = time.time()

        if self.output_controller.verbose:
            print_info(f"🔍 Enriching {len(asg_groups)} Auto Scaling Groups with A1-A5 activity signals...")

        # Delegate to existing ASGActivityEnricher (KISS/DRY/LEAN - reuse proven code)
        enriched = self.asg_enricher.enrich_asg_activity(asg_groups)

        # Update stats
        self._enrichment_stats['asg_count'] = len(enriched)
        elapsed = time.time() - start_time
        self._enrichment_stats['total_time'] += elapsed

        if self.output_controller.verbose:
            print_success(f"✅ ASG activity enrichment complete: {len(enriched)} resources, {elapsed:.2f}s")

        return enriched

    def enrich_alb_activity(self, load_balancers: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich ALB/NLB with L1-L5 activity signals.

        Delegates to ALBActivityEnricher (inventory/enrichers/alb_activity_enricher.py) for:
        - L1: Zero active connections (45 points) - No connections for 90+ days
        - L2: Low request count (25 points) - <100 requests/day average
        - L3: No healthy targets (15 points) - All targets unhealthy for 30+ days
        - L4: Low data transfer (10 points) - <100 MB/day transferred
        - L5: High error rate (5 points) - >50% 4XX/5XX errors

        Args:
            load_balancers: DataFrame with load_balancer_arn column (from discovery)

        Returns:
            Enhanced DataFrame with ALB/NLB activity columns and L1-L5 signals

        Performance:
            - Graceful degradation on empty input
            - CloudWatch metrics collection (90-day window)
            - Decommission scoring (MUST/SHOULD/COULD/KEEP)

        Example:
            >>> df = pd.DataFrame({'load_balancer_arn': ['arn:aws:...']})
            >>> enriched = enricher.enrich_alb_activity(df)
            >>> print(enriched.columns)
            # Shows: load_balancer_arn, active_connection_count_90d, l1_signal, ...
        """
        if load_balancers.empty:
            if self.output_controller.verbose:
                print_warning("⚠️  No load balancers to enrich")
            return load_balancers

        start_time = time.time()

        if self.output_controller.verbose:
            print_info(f"🔍 Enriching {len(load_balancers)} load balancers with L1-L5 activity signals...")

        # Delegate to existing ALBActivityEnricher (KISS/DRY/LEAN - reuse proven code)
        # Works for both ALB and NLB (same ELBv2 API, different CloudWatch namespaces)
        enriched = self.alb_enricher.enrich_alb_activity(load_balancers)

        # Update stats
        self._enrichment_stats['alb_count'] = len(enriched)
        elapsed = time.time() - start_time
        self._enrichment_stats['total_time'] += elapsed

        if self.output_controller.verbose:
            print_success(f"✅ Load balancer activity enrichment complete: {len(enriched)} resources, {elapsed:.2f}s")

        return enriched

    def enrich_s3_activity(self, s3_buckets: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich S3 buckets with S1-S7 activity signals.

        Delegates to S3LifecycleOptimizer (finops/s3_lifecycle_optimizer.py) for:
        - S1 (20 pts): No lifecycle policy configured
        - S2 (15 pts): STANDARD storage unoptimized (IA/Glacier candidates)
        - S3 (12 pts): Glacier candidate (>90d unaccessed)
        - S4 (10 pts): Deep Archive candidate (>365d unaccessed)
        - S5 (8 pts): Versioning without expiration policy
        - S6 (7 pts): Temp/log data without expiration
        - S7 (3 pts): Cost efficiency score

        Args:
            s3_buckets: DataFrame with bucket_name column (from discovery)

        Returns:
            Enhanced DataFrame with S3 activity columns and S1-S7 signals

        Performance:
            - Graceful degradation on empty input
            - CloudWatch metrics + S3 API analysis
            - Decommission scoring (MUST/SHOULD/COULD/KEEP)

        Example:
            >>> df = pd.DataFrame({'bucket_name': ['my-bucket-1', 'my-bucket-2']})
            >>> enriched = enricher.enrich_s3_activity(df)
            >>> print(enriched.columns)
            # Shows: bucket_name, s1_lifecycle_policy, s2_storage_unoptimized, ...
        """
        if s3_buckets.empty:
            if self.output_controller.verbose:
                print_warning("⚠️  No S3 buckets to enrich")
            return s3_buckets

        if not S3_AVAILABLE:
            if self.output_controller.verbose:
                print_warning("⚠️  S3LifecycleOptimizer not available - skipping S3 enrichment")
            return s3_buckets

        start_time = time.time()

        if self.output_controller.verbose:
            print_info(f"🔍 Enriching {len(s3_buckets)} S3 buckets with S1-S7 activity signals...")

        try:
            # Run S3 lifecycle optimization analysis (async)
            import asyncio
            analysis_results = asyncio.run(
                self.s3_analyzer.analyze_s3_lifecycle_optimization(dry_run=True)
            )

            # Extract S1-S7 signals from analysis
            bucket_signals = self.s3_analyzer.extract_activity_signals(
                buckets=analysis_results.analyzed_buckets,
                access_analysis=analysis_results.access_analysis,
                recommendations=analysis_results.recommendations
            )

            # Merge signals into DataFrame
            enriched = s3_buckets.copy()

            # Add signal columns
            for signal in ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7']:
                enriched[signal] = enriched['bucket_name'].apply(
                    lambda bn: bucket_signals.get(bn, {}).get(signal, 0)
                )

            # Calculate total score using decommission scorer
            from runbooks.finops.decommission_scorer import calculate_s3_score

            def calculate_bucket_score(row):
                signals = {
                    'S1': row['S1'],
                    'S2': row['S2'],
                    'S3': row['S3'],
                    'S4': row['S4'],
                    'S5': row['S5'],
                    'S6': row['S6'],
                    'S7': row['S7']
                }
                result = calculate_s3_score(signals)
                return pd.Series({
                    'decommission_score': result['total_score'],
                    'decommission_tier': result['tier'],
                    'recommendation': result['recommendation'],
                    'confidence': result['confidence']
                })

            enriched[['decommission_score', 'decommission_tier', 'recommendation', 'confidence']] = \
                enriched.apply(calculate_bucket_score, axis=1)

            # Add bucket metadata (total_size_gb, age_days, last_access_days) from analyzed_buckets
            from datetime import datetime, timezone

            # Build access_analysis lookup for last_access_date (access_analysis is a dict)
            access_lookup = {
                bucket_name: access_obj.last_access_date
                for bucket_name, access_obj in analysis_results.access_analysis.items()
            }

            bucket_metadata = {
                b.bucket_name: {
                    'total_size_gb': b.total_size_gb,
                    'total_objects': b.total_objects,
                    'age_days': (datetime.now(timezone.utc) - b.creation_date).days,
                    'last_access_days': (
                        (datetime.now(timezone.utc) - access_lookup.get(b.bucket_name)).days
                        if access_lookup.get(b.bucket_name) else None
                    )
                }
                for b in analysis_results.analyzed_buckets
            }

            enriched['total_size_gb'] = enriched['bucket_name'].apply(
                lambda bn: bucket_metadata.get(bn, {}).get('total_size_gb', 0.0)
            )
            enriched['total_objects'] = enriched['bucket_name'].apply(
                lambda bn: bucket_metadata.get(bn, {}).get('total_objects', 0)
            )
            enriched['age_days'] = enriched['bucket_name'].apply(
                lambda bn: bucket_metadata.get(bn, {}).get('age_days', 0)
            )
            enriched['last_access_days'] = enriched['bucket_name'].apply(
                lambda bn: bucket_metadata.get(bn, {}).get('last_access_days')
            )

            # Calculate monthly cost (STANDARD storage pricing: $0.025/GB/month)
            enriched['monthly_cost'] = enriched['total_size_gb'].apply(
                lambda size_gb: size_gb * 0.025
            )

            # Update stats
            self._enrichment_stats['s3_count'] = len(enriched)
            elapsed = time.time() - start_time
            self._enrichment_stats['total_time'] += elapsed

            if self.output_controller.verbose:
                print_success(f"✅ S3 activity enrichment complete: {len(enriched)} buckets, {elapsed:.2f}s")

            return enriched

        except Exception as e:
            if self.output_controller.verbose:
                print_error(f"S3 enrichment failed: {str(e)}")
            logger.error(f"S3 enrichment error: {e}", exc_info=True)
            return s3_buckets

    def enrich_dx_activity(self, dx_connections: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich Direct Connect connections with DX1-DX4 activity signals.

        Delegates to DXActivityEnricher (inventory/enrichers/dx_activity_enricher.py) for:
        - DX1 (60 pts): Connection down state
        - DX2 (20 pts): Low bandwidth utilization (<10%)
        - DX3 (10 pts): No BGP routes
        - DX4 (10 pts): No data transfer 90+ days

        Args:
            dx_connections: DataFrame with connection_id column (from discovery)

        Returns:
            Enhanced DataFrame with DX activity columns and DX1-DX4 signals

        Performance:
            - Graceful degradation on empty input
            - CloudWatch metrics + Direct Connect API analysis
            - Decommission scoring (MUST/SHOULD/COULD/KEEP)

        Example:
            >>> df = pd.DataFrame({'connection_id': ['dxcon-abc123']})
            >>> enriched = enricher.enrich_dx_activity(df)
            >>> print(enriched.columns)
            # Shows: connection_id, dx1_down_state, dx2_low_utilization, ...
        """
        if dx_connections.empty:
            if self.output_controller.verbose:
                print_warning("⚠️  No Direct Connect connections to enrich")
            return dx_connections

        start_time = time.time()

        if self.output_controller.verbose:
            print_info(f"🔍 Enriching {len(dx_connections)} Direct Connect connections with DX1-DX4 signals...")

        # Delegate to existing DXActivityEnricher (KISS/DRY/LEAN - reuse proven code)
        enriched = self.dx_enricher.enrich_dx_activity(dx_connections)

        # Update stats
        self._enrichment_stats['dx_count'] = len(enriched)
        elapsed = time.time() - start_time
        self._enrichment_stats['total_time'] += elapsed

        if self.output_controller.verbose:
            print_success(f"✅ Direct Connect activity enrichment complete: {len(enriched)} connections, {elapsed:.2f}s")

        return enriched

    def enrich_route53_activity(self, hosted_zones: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich Route53 hosted zones with R53-1 to R53-4 activity signals.

        Delegates to Route53ActivityEnricher (inventory/enrichers/route53_activity_enricher.py) for:
        - R53-1 (40 pts): Zero DNS queries 30+ days
        - R53-2 (30 pts): Health check failures
        - R53-3 (20 pts): No record updates 365+ days
        - R53-4 (10 pts): Orphaned hosted zone (0 records)

        Args:
            hosted_zones: DataFrame with hosted_zone_id column (from discovery)

        Returns:
            Enhanced DataFrame with Route53 activity columns and R53-1 to R53-4 signals

        Performance:
            - Graceful degradation on empty input
            - CloudWatch metrics + Route53 API analysis
            - Decommission scoring (MUST/SHOULD/COULD/KEEP)

        Example:
            >>> df = pd.DataFrame({'hosted_zone_id': ['Z1234567890ABC']})
            >>> enriched = enricher.enrich_route53_activity(df)
            >>> print(enriched.columns)
            # Shows: hosted_zone_id, r53_1_zero_queries, r53_2_health_failures, ...
        """
        if hosted_zones.empty:
            if self.output_controller.verbose:
                print_warning("⚠️  No Route53 hosted zones to enrich")
            return hosted_zones

        start_time = time.time()

        if self.output_controller.verbose:
            print_info(f"🔍 Enriching {len(hosted_zones)} Route53 hosted zones with R53-1 to R53-4 signals...")

        # Delegate to existing Route53ActivityEnricher (KISS/DRY/LEAN - reuse proven code)
        enriched = self.route53_enricher.enrich_route53_activity(hosted_zones)

        # Update stats
        self._enrichment_stats['route53_count'] = len(enriched)
        elapsed = time.time() - start_time
        self._enrichment_stats['total_time'] += elapsed

        if self.output_controller.verbose:
            print_success(f"✅ Route53 activity enrichment complete: {len(enriched)} zones, {elapsed:.2f}s")

        return enriched

    def enrich_vpc_activity(self, vpc_resources: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich VPC resources with V1-V5/N1-N5 activity signals (all 4 resource types).

        Delegates to specialized enrichers for:
        - VPC Endpoints (VPCE): V1-V5 signals (zero data transfer, idle endpoints)
        - VPC Peering: V1-V5 signals (zero data transfer, unused peering connections)
        - Transit Gateways: V1-V5 signals (zero data transfer, idle attachments)
        - NAT Gateways: N1-N5 signals (zero data transfer, idle NAT gateways)

        Args:
            vpc_resources: DataFrame with resource_type column distinguishing 4 types:
                           'vpce', 'vpc_peering', 'transit_gateway', 'nat_gateway'

        Returns:
            Enhanced DataFrame with VPC activity columns and V1-V5/N1-N5 signals

        Performance:
            - Graceful degradation on empty input
            - CloudWatch metrics + VPC API analysis
            - Decommission scoring (MUST/SHOULD/COULD/KEEP)
            - Dynamic denominator support (100 with CloudWatch, 60 without)

        Example:
            >>> df = pd.DataFrame({
            ...     'resource_type': ['vpce', 'nat_gateway'],
            ...     'resource_id': ['vpce-abc123', 'nat-def456']
            ... })
            >>> enriched = enricher.enrich_vpc_activity(df)
            >>> print(enriched['decommission_tier'].value_counts())
            # Shows: MUST/SHOULD/COULD/KEEP distribution
        """
        if vpc_resources.empty:
            if self.output_controller.verbose:
                print_warning("⚠️  No VPC resources to enrich")
            return vpc_resources

        start_time = time.time()

        if self.output_controller.verbose:
            print_info(f"🔍 Enriching {len(vpc_resources)} VPC resources with V1-V5/N1-N5 signals...")

        # Split by resource type and delegate to specialized enrichers
        enriched_parts = []

        if 'resource_type' in vpc_resources.columns:
            # VPC Endpoints (VPCE)
            vpce_df = vpc_resources[vpc_resources['resource_type'] == 'vpce'].copy()
            if not vpce_df.empty:
                # Rename resource_id → vpc_endpoint_id (enricher requirement)
                vpce_df['vpc_endpoint_id'] = vpce_df['resource_id']
                enriched_vpce = self.vpce_enricher.enrich_vpce_activity(vpce_df)
                enriched_parts.append(enriched_vpce)

            # VPC Peering
            peering_df = vpc_resources[vpc_resources['resource_type'] == 'vpc_peering'].copy()
            if not peering_df.empty:
                # Rename resource_id → vpc_peering_connection_id (enricher requirement)
                peering_df['vpc_peering_connection_id'] = peering_df['resource_id']
                enriched_peering = self.vpc_peering_enricher.enrich_vpc_peering_activity(peering_df)
                enriched_parts.append(enriched_peering)

            # Transit Gateways
            tgw_df = vpc_resources[vpc_resources['resource_type'] == 'transit_gateway'].copy()
            if not tgw_df.empty:
                # Rename resource_id → transit_gateway_id (enricher requirement)
                tgw_df['transit_gateway_id'] = tgw_df['resource_id']
                enriched_tgw = self.transit_gateway_enricher.enrich_transit_gateway_activity(tgw_df)
                enriched_parts.append(enriched_tgw)

            # NAT Gateways
            nat_df = vpc_resources[vpc_resources['resource_type'] == 'nat_gateway'].copy()
            if not nat_df.empty:
                # Rename resource_id → nat_gateway_id (enricher requirement)
                nat_df['nat_gateway_id'] = nat_df['resource_id']
                enriched_nat = self.nat_gateway_enricher.enrich_nat_gateway_activity(nat_df)
                enriched_parts.append(enriched_nat)

        # Combine all enriched parts
        if enriched_parts:
            enriched = pd.concat(enriched_parts, ignore_index=True)
        else:
            if self.output_controller.verbose:
                print_warning("⚠️  No recognized VPC resource types found")
            return vpc_resources

        # Update stats
        self._enrichment_stats['vpc_count'] = len(enriched)
        elapsed = time.time() - start_time
        self._enrichment_stats['total_time'] += elapsed

        if self.output_controller.verbose:
            print_success(f"✅ VPC activity enrichment complete: {len(enriched)} resources, {elapsed:.2f}s")

        return enriched

    def enrich_all_resources(self, discovery_results: Dict) -> Dict[str, pd.DataFrame]:
        """
        Orchestrate activity enrichment for all resource types.

        Coordinates enrichment across EC2, RDS, DynamoDB, and S3 (if available) using
        specialized enrichers with graceful degradation.

        Args:
            discovery_results: Dictionary with resource discovery DataFrames
                {
                    'ec2': DataFrame with instance_id column,
                    'rds': DataFrame with db_instance_id column,
                    'dynamodb': DataFrame with table_name column,
                    's3': DataFrame with bucket_name column (optional)
                }

        Returns:
            Dictionary with enriched DataFrames:
                {
                    'ec2': Enhanced EC2 DataFrame with 11 activity columns,
                    'rds': Enhanced RDS DataFrame with R1-R7 signals,
                    'dynamodb': Enhanced DynamoDB DataFrame with D1-D5 signals,
                    's3': Enhanced S3 DataFrame with S1-S7 signals (if available)
                }

        Performance:
            - Lazy enricher initialization (only loaded when needed)
            - Graceful degradation (skips empty resource types)
            - Progress tracking via OutputController verbose flag
            - Statistics collection for monitoring

        Example:
            >>> discovery = {
            ...     'ec2': pd.DataFrame({'instance_id': ['i-abc123']}),
            ...     'rds': pd.DataFrame({'db_instance_id': ['mydb-1']})
            ... }
            >>> enriched = enricher.enrich_all_resources(discovery)
            >>> print(enriched['ec2'].shape)  # Shows enriched columns
            >>> print(enriched['rds']['idle_signals'].tolist())  # Shows R1-R7 signals
        """
        start_time = time.time()
        enriched = {}

        if self.output_controller.verbose:
            print_info("🎯 Starting multi-resource activity enrichment...")

        # EC2 enrichment (11 activity columns from 4 AWS services)
        if 'ec2' in discovery_results and not discovery_results['ec2'].empty:
            enriched['ec2'] = self.enrich_ec2_activity(discovery_results['ec2'])
        elif 'ec2' in discovery_results:
            if self.output_controller.verbose:
                print_warning("⏭️  Skipping EC2 enrichment (no instances)")
            enriched['ec2'] = discovery_results['ec2']

        # RDS enrichment (R1-R7 database activity signals)
        if 'rds' in discovery_results and not discovery_results['rds'].empty:
            enriched['rds'] = self.enrich_rds_activity(discovery_results['rds'])
        elif 'rds' in discovery_results:
            if self.output_controller.verbose:
                print_warning("⏭️  Skipping RDS enrichment (no instances)")
            enriched['rds'] = discovery_results['rds']

        # DynamoDB enrichment (D1-D5 NoSQL database activity signals)
        if 'dynamodb' in discovery_results and not discovery_results['dynamodb'].empty:
            enriched['dynamodb'] = self.enrich_dynamodb_activity(discovery_results['dynamodb'])
        elif 'dynamodb' in discovery_results:
            if self.output_controller.verbose:
                print_warning("⏭️  Skipping DynamoDB enrichment (no tables)")
            enriched['dynamodb'] = discovery_results['dynamodb']

        # ASG enrichment (A1-A5 Auto Scaling Group activity signals)
        if 'asg' in discovery_results and not discovery_results['asg'].empty:
            enriched['asg'] = self.enrich_asg_activity(discovery_results['asg'])
        elif 'asg' in discovery_results:
            if self.output_controller.verbose:
                print_warning("⏭️  Skipping ASG enrichment (no Auto Scaling Groups)")
            enriched['asg'] = discovery_results['asg']

        # ALB/NLB enrichment (L1-L5 load balancer activity signals)
        if 'alb' in discovery_results and not discovery_results['alb'].empty:
            enriched['alb'] = self.enrich_alb_activity(discovery_results['alb'])
        elif 'alb' in discovery_results:
            if self.output_controller.verbose:
                print_warning("⏭️  Skipping ALB/NLB enrichment (no load balancers)")
            enriched['alb'] = discovery_results['alb']

        # S3 enrichment (if S3LifecycleOptimizer available)
        if 's3' in discovery_results and S3_AVAILABLE and not discovery_results['s3'].empty:
            enriched['s3'] = self.enrich_s3_activity(discovery_results['s3'])
        elif 's3' in discovery_results:
            if self.output_controller.verbose:
                if not S3_AVAILABLE:
                    print_warning("⏭️  Skipping S3 enrichment (S3LifecycleOptimizer not available)")
                else:
                    print_warning("⏭️  Skipping S3 enrichment (no buckets)")
            enriched['s3'] = discovery_results['s3']

        # Direct Connect enrichment (DX1-DX4 signals)
        if 'dx' in discovery_results and not discovery_results['dx'].empty:
            enriched['dx'] = self.enrich_dx_activity(discovery_results['dx'])
        elif 'dx' in discovery_results:
            if self.output_controller.verbose:
                print_warning("⏭️  Skipping DX enrichment (no connections)")
            enriched['dx'] = discovery_results['dx']

        # Route53 enrichment (R53-1 to R53-4 signals)
        if 'route53' in discovery_results and not discovery_results['route53'].empty:
            enriched['route53'] = self.enrich_route53_activity(discovery_results['route53'])
        elif 'route53' in discovery_results:
            if self.output_controller.verbose:
                print_warning("⏭️  Skipping Route53 enrichment (no hosted zones)")
            enriched['route53'] = discovery_results['route53']

        # VPC enrichment (V1-V5/N1-N5 network connectivity signals - 4 resource types)
        if 'vpc' in discovery_results and not discovery_results['vpc'].empty:
            enriched['vpc'] = self.enrich_vpc_activity(discovery_results['vpc'])
        elif 'vpc' in discovery_results:
            if self.output_controller.verbose:
                print_warning("⏭️  Skipping VPC enrichment (no resources)")
            enriched['vpc'] = discovery_results['vpc']

        # Calculate total execution time
        total_time = time.time() - start_time
        self._enrichment_stats['total_time'] = total_time

        # Display summary
        if self.output_controller.verbose:
            self._display_enrichment_summary()

        return enriched

    def _display_enrichment_summary(self) -> None:
        """
        Display enrichment statistics summary.

        Shows:
            - Total resources enriched per type
            - Total execution time
            - Performance metrics
        """
        stats = self._enrichment_stats

        summary_lines = [
            "✅ Multi-resource activity enrichment complete",
            f"   EC2: {stats['ec2_count']} instances enriched",
            f"   RDS: {stats['rds_count']} instances enriched",
            f"   DynamoDB: {stats['dynamodb_count']} tables enriched",
            f"   ASG: {stats['asg_count']} Auto Scaling Groups enriched",
            f"   ALB/NLB: {stats['alb_count']} load balancers enriched",
            f"   S3: {stats['s3_count']} buckets enriched",
            f"   DX: {stats['dx_count']} Direct Connect connections enriched",
            f"   Route53: {stats['route53_count']} hosted zones enriched",
            f"   Total time: {stats['total_time']:.2f}s"
        ]

        for line in summary_lines:
            print_success(line)

    def get_enrichment_stats(self) -> Dict:
        """
        Get enrichment statistics.

        Returns:
            Dictionary with enrichment statistics:
                {
                    'ec2_count': Number of EC2 instances enriched,
                    'rds_count': Number of RDS instances enriched,
                    'dynamodb_count': Number of DynamoDB tables enriched,
                    'alb_count': Number of ALB/NLB enriched,
                    's3_count': Number of S3 buckets enriched,
                    'total_time': Total execution time in seconds
                }
        """
        return self._enrichment_stats.copy()


# Factory function for clean initialization
def create_dashboard_activity_enricher(
    operational_profile: str,
    region: str = "ap-southeast-2",
    verbose: bool = False,
    lookback_days: int = 90
) -> DashboardActivityEnricher:
    """
    Factory function to create DashboardActivityEnricher.

    Provides clean initialization pattern following enterprise architecture
    with automatic OutputController configuration.

    Args:
        operational_profile: AWS profile for operational account
        region: AWS region (default: ap-southeast-2)
        verbose: Enable verbose debug output (default: False)
        lookback_days: CloudWatch lookback period (default: 90)

    Returns:
        Initialized DashboardActivityEnricher instance

    Example:
        >>> enricher = create_dashboard_activity_enricher(
        ...     operational_profile='ops-profile',
        ...     verbose=True
        ... )
        >>> # Enricher ready for orchestration
        >>> enriched = enricher.enrich_all_resources(discovery)
    """
    output_controller = OutputController(verbose=verbose)

    return DashboardActivityEnricher(
        operational_profile=operational_profile,
        region=region,
        output_controller=output_controller,
        lookback_days=lookback_days
    )


# Export interface
__all__ = [
    "DashboardActivityEnricher",
    "create_dashboard_activity_enricher",
]

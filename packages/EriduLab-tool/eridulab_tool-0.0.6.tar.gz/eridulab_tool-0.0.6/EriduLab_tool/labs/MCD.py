import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MCD:
    """
    Mock Cloud Data Generator (MCD) with a fluent API.
    Generates a 'FOCUS-like' compliant dataset.
    """

    def __init__(self):
        # Default parameters
        self._days = 90
        self._instance_count = 200
        self._time_step_hours = 1
        self._risk_tolerance = 0.5
        self._random_state = None
        self._start_date = datetime(2024, 10, 1)

        # Controllable parameters
        self._storage_ratio = 0.2
        self._spike_probability = 0.1
        self._idle_ratio = 0.1 # New default
        self._overprovisioned_ratio = 0.15 # New default

    # --- Standard Fluent Methods ---
    def days(self, days: int):
        if not isinstance(days, int) or days <= 0:
            raise ValueError("Days must be a positive integer.")
        self._days = days
        return self

    def risk(self, risk_level: float):
        if not isinstance(risk_level, (float, int)) or not (0.0 <= risk_level <= 1.0):
            raise ValueError("Risk level must be a float between 0.0 and 1.0.")
        self._risk_tolerance = risk_level
        return self

    def inst(self, instance_count: int):
        if not isinstance(instance_count, int) or instance_count <= 0:
            raise ValueError("Instance count must be a positive integer.")
        self._instance_count = instance_count
        return self

    def Rs(self, random_state: int):
        if random_state is not None and not isinstance(random_state, int):
            raise ValueError("Random state must be an integer or None.")
        self._random_state = random_state
        return self

    def start_date(self, start_date: datetime):
        if not isinstance(start_date, datetime):
            raise ValueError("Start date must be a datetime object.")
        self._start_date = start_date
        return self

    # --- Advanced Control Fluent Methods ---
    def with_storage_ratio(self, ratio: float):
        """
        Sets the ratio of storage resources to generate.
        :param ratio: A float between 0.0 and 1.0. (e.g., 0.3 = 30% storage, 70% VM)
        """
        if not isinstance(ratio, (float, int)) or not (0.0 <= ratio <= 1.0):
            raise ValueError("Storage ratio must be a float between 0.0 and 1.0.")
        self._storage_ratio = ratio
        return self

    def with_anomaly_rate(self, probability: float):
        """
        Sets the probability for a VM to be "spiky" (anomalous).
        :param probability: A float between 0.0 and 1.0. (e.g., 0.15 = 15% of VMs will be spiky)
        """
        if not isinstance(probability, (float, int)) or not (0.0 <= probability <= 1.0):
            raise ValueError("Anomaly rate probability must be a float between 0.0 and 1.0.")
        self._spike_probability = probability
        return self

    def with_idle_ratio(self, ratio: float):
        """
        Sets the target ratio of VM instances to be marked as idle.
        :param ratio: A float between 0.0 and 1.0.
        """
        if not isinstance(ratio, (float, int)) or not (0.0 <= ratio <= 1.0):
            raise ValueError("Idle ratio must be a float between 0.0 and 1.0.")
        self._idle_ratio = ratio
        return self

    def with_overprovisioned_ratio(self, ratio: float):
        """
        Sets the target ratio of VM instances to be marked as overprovisioned.
        :param ratio: A float between 0.0 and 1.0.
        """
        if not isinstance(ratio, (float, int)) or not (0.0 <= ratio <= 1.0):
            raise ValueError("Overprovisioned ratio must be a float between 0.0 and 1.0.")
        self._overprovisioned_ratio = ratio
        return self

    # --- Generation Method ---
    def gen(self) -> pd.DataFrame:
        """Generates the mock cloud dataset based on the configured parameters."""

        rng = np.random.default_rng(self._random_state)
        time_intervals = pd.date_range(
            start=self._start_date,
            periods=int(self._days * 24 / self._time_step_hours),
            freq=f'{self._time_step_hours}h'
        )
        resource_ids = [f"res:{i:04d}" for i in range(self._instance_count)]
        resource_data = []

        # Determine idle and overprovisioned instances based on new ratios
        num_idle_vms = int(self._instance_count * self._idle_ratio)
        num_overprovisioned_vms = int(self._instance_count * self._overprovisioned_ratio)

        # Ensure we don't assign too many, and idle takes priority if both are possible for a resource
        idle_indices = rng.choice(self._instance_count, size=num_idle_vms, replace=False)
        remaining_indices = np.setdiff1d(np.arange(self._instance_count), idle_indices)
        overprovisioned_indices = rng.choice(remaining_indices, size=min(num_overprovisioned_vms, len(remaining_indices)), replace=False)

        for i, res_id in enumerate(resource_ids):
            instance_rng = np.random.default_rng(self._random_state + i if self._random_state is not None else None)
            project_id = instance_rng.choice([f"proj-{j}" for j in range(1, 16)])
            region = instance_rng.choice(['us-east-1', 'us-west-2', 'eu-central-1', 'ap-southeast-1'])

            env_tag = instance_rng.choice(['prod', 'dev', 'staging'], p=[0.6, 0.3, 0.1])
            tags = {'project': project_id, 'env': env_tag}

            vm_ratio = 1.0 - self._storage_ratio
            if instance_rng.random() < vm_ratio:
                # --- VM Resource ---
                resource_type_group = 'VM'
                service_name = 'EriduCompute'
                consumed_unit = 'Hours'
                resource_type = instance_rng.choice(['n2-standard-8', 'e2-medium', 'c2-standard-16', 'm1-ultramem-40'])
                cpu_cores = int(resource_type.split('-')[-1]) if 'standard' in resource_type else instance_rng.choice([2,4,8,16])
                max_memory_gb = cpu_cores * instance_rng.uniform(2, 4)
                if 'n2-standard' in resource_type: list_cost_per_hour = instance_rng.uniform(0.2, 0.4)
                elif 'e2-medium' in resource_type: list_cost_per_hour = instance_rng.uniform(0.05, 0.15)
                elif 'c2-standard' in resource_type: list_cost_per_hour = instance_rng.uniform(0.5, 0.8)
                else: list_cost_per_hour = instance_rng.uniform(0.1, 0.5)

                # Use new idle/overprovisioned logic
                is_idle = i in idle_indices
                is_overprovisioned = (not is_idle) and (i in overprovisioned_indices)

            else:
                # --- Storage Resource ---
                resource_type_group = 'Storage'
                service_name = 'EriduStorage'
                consumed_unit = 'Transactions'
                resource_type = instance_rng.choice(['S3-Standard', 'Blob-Cool', 'CloudStorage-Archival'])
                cpu_cores = 0
                max_memory_gb = 0
                list_cost_per_hour = instance_rng.uniform(0.001, 0.005)
                is_idle = False
                is_overprovisioned = False

            # Pricing and Cost Logic (unchanged)
            if self._risk_tolerance < 0.2:
                pricing_category = instance_rng.choice(['OnDemand', 'Reservation'], p=[0.7, 0.3])
            elif self._risk_tolerance < 0.6:
                pricing_category = instance_rng.choice(['OnDemand', 'Reservation', 'Spot'], p=[0.4, 0.4, 0.2])
            else:
                pricing_category = instance_rng.choice(['OnDemand', 'Reservation', 'Spot'], p=[0.2, 0.3, 0.5])

            if pricing_category == 'Reservation':
                effective_cost_multiplier = instance_rng.uniform(0.5, 0.7)
            elif pricing_category == 'Spot':
                effective_cost_multiplier = instance_rng.uniform(0.1, 0.3)
            else:
                effective_cost_multiplier = 1.0
            effective_cost = list_cost_per_hour * effective_cost_multiplier
            config_risk_factor = np.clip(instance_rng.uniform(0.1, 0.8) * (1 + self._risk_tolerance), 0.1, 1.0)
            is_spiky = instance_rng.random() < self._spike_probability and resource_type_group == 'VM'

            resource_data.append({
                'ResourceID': res_id, 'ProjectID': project_id, 'Region': region,
                'ResourceType': resource_type, 'ResourceTypeGroup': resource_type_group,
                'PricingCategory': pricing_category, 'ListCost_Per_Hour': list_cost_per_hour,
                'EffectiveCost_Base': effective_cost, 'CPU_Cores': cpu_cores,
                'Max_Memory_GB': max_memory_gb, 'Config_Risk_Factor': config_risk_factor,
                'Is_Idle': is_idle, 'Is_Overprovisioned': is_overprovisioned,
                'Is_Spiky': is_spiky,
                'ServiceName': service_name,
                'ConsumedUnit': consumed_unit,
                'Tags': tags
            })

        resource_df = pd.DataFrame(resource_data)
        all_data = []

        # Metrics Generation Loop
        for _, res_row in resource_df.iterrows():
            resource_id = res_row['ResourceID']
            instance_rng = np.random.default_rng(self._random_state + int(resource_id.split(':')[-1]) if self._random_state is not None else None)

            if res_row['ResourceTypeGroup'] == 'VM':
                base_cpu_utilization = instance_rng.uniform(10, 60)
                if res_row['Is_Idle']: base_cpu_utilization = instance_rng.uniform(5, 25)
                elif res_row['Is_Overprovisioned']: base_cpu_utilization = instance_rng.uniform(20, 50)

                cpu_utilization_pattern = np.sin(np.linspace(0, 2 * np.pi * self._days, len(time_intervals))) * 20
                cpu_utilization = base_cpu_utilization + cpu_utilization_pattern + instance_rng.normal(0, 5, len(time_intervals))

                if res_row['Is_Spiky']:
                    spike_hours = instance_rng.choice(len(time_intervals), size=int(len(time_intervals) * 0.005), replace=False)
                    spike_magnitudes = instance_rng.uniform(50, 80, size=len(spike_hours))
                    cpu_utilization[spike_hours] += spike_magnitudes

                cpu_utilization = np.clip(cpu_utilization, 0, 100)
                memory_usage_gb = np.clip(
                    (cpu_utilization / 100) * res_row['Max_Memory_GB'] * instance_rng.uniform(0.7, 1.2) + instance_rng.normal(0, 1),
                    0, res_row['Max_Memory_GB']
                )
                consumed_quantity = np.ones(len(time_intervals))
                operational_risk_score = np.clip(
                    res_row['Config_Risk_Factor'] * (1 + self._risk_tolerance * 0.5)
                    + (cpu_utilization / 100) * instance_rng.uniform(0.05, 0.15)
                    + (1 if res_row['Is_Idle'] else 0) * instance_rng.uniform(0.05, 0.1)
                    + (1 if res_row['Is_Overprovisioned'] else 0) * instance_rng.uniform(0.02, 0.05)
                    + instance_rng.normal(0, 0.05), 0.01, 1.0
                )
            else:
                base_transactions = instance_rng.poisson(lam=100, size=len(time_intervals))
                spike_hours = instance_rng.choice(len(time_intervals), size=int(len(time_intervals) * 0.02), replace=False)
                base_transactions[spike_hours] += instance_rng.poisson(lam=1000, size=len(spike_hours))
                consumed_quantity = base_transactions
                cpu_utilization = np.zeros(len(time_intervals))
                memory_usage_gb = np.zeros(len(time_intervals))
                operational_risk_score = np.clip(
                    res_row['Config_Risk_Factor'] * (1 + self._risk_tolerance * 0.2)
                    + (consumed_quantity / 1000) * instance_rng.uniform(0.01, 0.05)
                    + instance_rng.normal(0, 0.01), 0.01, 1.0
                )
                is_idle, is_overprovisioned = False, False

            if res_row['ResourceTypeGroup'] == 'VM':
                hourly_effective_cost = res_row['EffectiveCost_Base'] * consumed_quantity
            else:
                hourly_effective_cost = res_row['EffectiveCost_Base'] * consumed_quantity
            billed_cost_daily_total = hourly_effective_cost * 24

            instance_hourly_data = pd.DataFrame({
                'TimeInterval': time_intervals, 'ResourceID': resource_id,
                'ProjectID': res_row['ProjectID'], 'Region': res_row['Region'],
                'ResourceType': res_row['ResourceType'], 'ResourceTypeGroup': res_row['ResourceTypeGroup'],
                'PricingCategory': res_row['PricingCategory'], 'ListCost_Per_Hour': res_row['ListCost_Per_Hour'],
                'EffectiveCost': hourly_effective_cost, 'BilledCost_Daily_Total': billed_cost_daily_total,
                'CPU_Cores': res_row['CPU_Cores'], 'Max_Memory_GB': res_row['Max_Memory_GB'],
                'ConsumedQuantity': consumed_quantity, 'CPU_Utilization_Pct': cpu_utilization,
                'Memory_Usage_GB': memory_usage_gb, 'Operational_Risk_Score': operational_risk_score,
                'Config_Risk_Factor': res_row['Config_Risk_Factor'], 'Is_Idle': is_idle,
                'Is_Overprovisioned': is_overprovisioned, 'Is_Spiky': res_row['Is_Spiky'],
                'ServiceName': res_row['ServiceName'],
                'ConsumedUnit': res_row['ConsumedUnit'],
                'Tags': [res_row['Tags']] * len(time_intervals)
            })
            all_data.append(instance_hourly_data)

        final_df = pd.concat(all_data, ignore_index=True)
        final_df['TimeInterval'] = pd.to_datetime(final_df['TimeInterval'])
        final_df = final_df.sort_values(by=['ResourceID', 'TimeInterval']).reset_index(drop=True)

        return final_df

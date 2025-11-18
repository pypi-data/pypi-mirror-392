import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MCD:
    """Mock Cloud Data Generator (MCD) with a fluent API."""

    def __init__(self):
        self._days = 90
        self._instance_count = 200
        self._time_step_hours = 1
        self._risk_tolerance = 0.5
        self._random_state = None
        self._start_date = datetime(2024, 10, 1)

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

    def gen(self) -> pd.DataFrame:
        """Generates the mock cloud dataset based on the configured parameters."""

        rng = np.random.default_rng(self._random_state)

        # 1. Time Series Generation
        time_intervals = pd.date_range(
            start=self._start_date,
            periods=int(self._days * 24 / self._time_step_hours), # Fixed: cast periods to int
            freq=f'{self._time_step_hours}h' # Fixed: changed 'H' to 'h'
        )

        # 2. Resource IDs and their stable attributes
        resource_ids = [f"vm-web:{i:04d}" for i in range(self._instance_count)]

        # Static attributes per instance
        resource_data = []
        for i, res_id in enumerate(resource_ids):
            # Ensure reproducibility even with varying instance counts
            instance_rng = np.random.default_rng(self._random_state + i if self._random_state is not None else None)

            project_id = instance_rng.choice([f"proj-{j}" for j in range(1, 16)])
            region = instance_rng.choice(['us-east-1', 'us-west-2', 'eu-central-1', 'ap-southeast-1'])
            resource_type = instance_rng.choice(['n2-standard-8', 'e2-medium', 'c2-standard-16', 'm1-ultramem-40'])
            cpu_cores = int(resource_type.split('-')[-1]) if 'standard' in resource_type else instance_rng.choice([2,4,8,16])
            max_memory_gb = cpu_cores * instance_rng.uniform(2, 4)

            # Pricing Category distribution influenced by risk tolerance
            # Higher risk_tolerance means more 'Spot' instances.
            if self._risk_tolerance < 0.2:
                pricing_category = instance_rng.choice(['OnDemand', 'Reservation'], p=[0.7, 0.3])
            elif self._risk_tolerance < 0.6:
                pricing_category = instance_rng.choice(['OnDemand', 'Reservation', 'Spot'], p=[0.4, 0.4, 0.2])
            else:
                pricing_category = instance_rng.choice(['OnDemand', 'Reservation', 'Spot'], p=[0.2, 0.3, 0.5])

            # Base List Cost per hour (vary by resource type)
            if 'n2-standard' in resource_type: list_cost_per_hour = instance_rng.uniform(0.2, 0.4)
            elif 'e2-medium' in resource_type: list_cost_per_hour = instance_rng.uniform(0.05, 0.15)
            elif 'c2-standard' in resource_type: list_cost_per_hour = instance_rng.uniform(0.5, 0.8)
            elif 'm1-ultramem' in resource_type: list_cost_per_hour = instance_rng.uniform(1.0, 2.5)
            else: list_cost_per_hour = instance_rng.uniform(0.1, 0.5)

            # Effective Cost based on pricing category (discount modeling)
            if pricing_category == 'Reservation':
                effective_cost_multiplier = instance_rng.uniform(0.5, 0.7) # 30-50% discount
            elif pricing_category == 'Spot':
                effective_cost_multiplier = instance_rng.uniform(0.1, 0.3) # 70-90% discount
            else: # OnDemand
                effective_cost_multiplier = 1.0
            effective_cost = list_cost_per_hour * effective_cost_multiplier

            # Configuration Risk Factor (static per instance)
            config_risk_factor = instance_rng.uniform(0.1, 0.8) * (1 + self._risk_tolerance) # Higher risk_tolerance => higher config risk
            config_risk_factor = np.clip(config_risk_factor, 0.1, 1.0)

            # Idle/Overprovisioned status (static per instance, influenced by risk tolerance)
            is_idle_prob = 0.05 + (0.15 * (1 - self._risk_tolerance)) # Lower risk_tolerance => more likely to be idle
            is_overprovisioned_prob = 0.05 + (0.15 * (1 - self._risk_tolerance)) # Lower risk_tolerance => more likely to be overprovisioned

            is_idle = instance_rng.random() < is_idle_prob
            is_overprovisioned = instance_rng.random() < is_overprovisioned_prob

            resource_data.append({
                'ResourceID': res_id,
                'ProjectID': project_id,
                'Region': region,
                'ResourceType': resource_type,
                'PricingCategory': pricing_category,
                'ListCost_Per_Hour': list_cost_per_hour,
                'EffectiveCost_Base': effective_cost, # Store base, will vary hourly
                'CPU_Cores': cpu_cores,
                'Max_Memory_GB': max_memory_gb,
                'Config_Risk_Factor': config_risk_factor,
                'Is_Idle': is_idle,
                'Is_Overprovisioned': is_overprovisioned
            })

        resource_df = pd.DataFrame(resource_data)

        # 3. Generate hourly metrics for each instance
        all_data = []
        for _, res_row in resource_df.iterrows():
            resource_id = res_row['ResourceID']
            instance_rng = np.random.default_rng(self._random_state + int(resource_id.split(':')[-1]) if self._random_state is not None else None)

            # Simulate CPU Utilization (more stable for non-idle/non-overprovisioned, lower for idle)
            base_cpu_utilization = instance_rng.uniform(10, 60)
            if res_row['Is_Idle']: base_cpu_utilization = instance_rng.uniform(5, 25) # Idle VMs have low base CPU
            elif res_row['Is_Overprovisioned']: base_cpu_utilization = instance_rng.uniform(20, 50) # Overprovisioned might have moderate
            
            # Add sinusoidal pattern for daily/weekly cycles
            cpu_utilization_pattern = np.sin(np.linspace(0, 2 * np.pi * self._days, len(time_intervals))) * 20
            cpu_utilization = np.clip(base_cpu_utilization + cpu_utilization_pattern + instance_rng.normal(0, 5, len(time_intervals)), 0, 100)

            # Simulate Memory Usage (correlated with CPU, but with its own noise)
            memory_usage_gb = np.clip(
                (cpu_utilization / 100) * res_row['Max_Memory_GB'] * instance_rng.uniform(0.7, 1.2) + instance_rng.normal(0, 1),
                0, res_row['Max_Memory_GB']
            )
            
            # Consumed Quantity (always 1 for a single VM instance)
            consumed_quantity = np.ones(len(time_intervals))

            # Operational Risk Score (dynamic, influenced by config risk and risk tolerance)
            # Higher CPU spikes or lower utilization in overprovisioned/idle might contribute
            operational_risk_score = (
                res_row['Config_Risk_Factor'] * (1 + self._risk_tolerance * 0.5) # Base from static config risk
                + (cpu_utilization / 100) * instance_rng.uniform(0.05, 0.15) # Dynamic based on CPU
                + (1 if res_row['Is_Idle'] else 0) * instance_rng.uniform(0.05, 0.1) # Idle adds a small fixed risk
                + (1 if res_row['Is_Overprovisioned'] else 0) * instance_rng.uniform(0.02, 0.05) # Overprovisioned adds a small fixed risk
                + instance_rng.normal(0, 0.05) # Random noise
            )
            operational_risk_score = np.clip(operational_risk_score, 0.01, 1.0)

            # Hourly Effective Cost (can vary slightly per hour based on operational factors or random fluct.)
            hourly_effective_cost = res_row['EffectiveCost_Base'] * instance_rng.uniform(0.95, 1.05, len(time_intervals))

            # Daily Billed Cost (for simulation, sum up hourly effective costs for the day)
            # This is tricky because it's a daily aggregate, but we are generating hourly data.
            # For simplicity, we'll calculate it for the current hour, assuming a daily rate applied to that hour's effective cost
            # A more complex model would aggregate over 24 hours.
            billed_cost_daily_total = hourly_effective_cost * 24 # Simplistic assumption for demonstration


            instance_hourly_data = pd.DataFrame({
                'TimeInterval': time_intervals,
                'ResourceID': resource_id,
                'ProjectID': res_row['ProjectID'],
                'Region': res_row['Region'],
                'ResourceType': res_row['ResourceType'],
                'PricingCategory': res_row['PricingCategory'],
                'ListCost_Per_Hour': res_row['ListCost_Per_Hour'],
                'EffectiveCost': hourly_effective_cost,
                'BilledCost_Daily_Total': billed_cost_daily_total,
                'CPU_Cores': res_row['CPU_Cores'],
                'Max_Memory_GB': res_row['Max_Memory_GB'],
                'ConsumedQuantity': consumed_quantity,
                'CPU_Utilization_Pct': cpu_utilization,
                'Memory_Usage_GB': memory_usage_gb,
                'Operational_Risk_Score': operational_risk_score,
                'Config_Risk_Factor': res_row['Config_Risk_Factor'],
                'Is_Idle': res_row['Is_Idle'],
                'Is_Overprovisioned': res_row['Is_Overprovisioned']
            })
            all_data.append(instance_hourly_data)

        final_df = pd.concat(all_data, ignore_index=True)
        # Ensure TimeInterval is datetime type
        final_df['TimeInterval'] = pd.to_datetime(final_df['TimeInterval'])
        # Sort for better readability and time-series consistency
        final_df = final_df.sort_values(by=['ResourceID', 'TimeInterval']).reset_index(drop=True)

        return final_df

print("Eridu/labs/MCD.py created successfully with the MCD class.")

// TypeScript Definitions matching FastAPI OpenAPI Schemas

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

export interface Store {
  id: string;
  name: string;
  city: string;
  location_type: string;
  store_size_sqft?: number;
  monthly_footfall?: number;
  income_index?: number;
  budget_affinity?: number;
  mid_range_affinity?: number;
  premium_affinity?: number;
  flagship_affinity?: number;
}

export interface StoreListResponse {
  stores: Store[];
  count: number;
}

export interface Product {
  id: string;
  brand?: string;
  model_name: string;
  segment: string;
  cost_price: number;
  retail_price: number;
  lifecycle_stage: string;
  markdown_percentage?: number;
  successor_product_id?: string | null;
  expected_successor_week?: number | null;
  launch_confidence?: number | null;
  is_rumoured?: boolean;
}

export interface ProductListResponse {
  products: Product[];
  count: number;
}

export interface InventoryRecord {
  store_id: string;
  product_id: string;
  current_stock: number;
  in_transit_stock: number;
  reserved_stock: number;
  target_stock_level?: number | null;
  reorder_point?: number | null;
  capital_allocated?: number | null;
  weeks_of_cover?: number | null;
}

export interface InventoryListResponse {
  records: InventoryRecord[];
  count: number;
  page?: number | null;
  page_size?: number | null;
}

export interface InventorySummary {
  total_units: number;
  raw_cost_value: number;
  operational_cost_value: number;
  total_retail_value: number;
  store_count: number;
  sku_count: number;
  capital_budget_limit: number;
  capital_headroom: number;
  capital_utilization_pct: number;
  four_week_sales_units?: number;
  four_week_demand_units?: number;
  four_week_revenue?: number;
  four_week_margin?: number;
  four_week_fill_rate?: number;
}

export interface ForecastRequest {
  store_id: string;
  product_id: string;
  planning_week: number;
}

export interface ForecastResponse {
  store_id: string;
  product_id: string;
  planning_week: number;
  forecast_weekly_demand: number;
  recent_sales_velocity: number;
  rolling_avg: number;
  trend_factor: number;
  seasonal_factor: number;
  lifecycle_factor: number;
  affinity_factor: number;
  confidence: number;
}

export interface AllocationRunRequest {
  planning_week: number;
  capital_budget_limit?: number;
  warehouse_available?: Record<string, number>;
}

export interface AllocationRecommendation {
  recommendation_id: string;
  planning_week: number;
  store_id: string;
  product_id: string;
  product_name: string;
  recommended_qty: number;
  current_stock: number;
  projected_stock: number;
  forecast_weekly_demand: number;
  current_woc: number;
  projected_woc: number;
  unit_marginal_value: number;
  total_net_benefit: number;
  total_avoided_goodwill_benefit: number;
  total_margin_contribution: number;
  total_allocation_cost: number;
  reason_code: string;
  headline: string;
  explanation_text: string;
  explanation_json: Record<string, any>;
}

export interface AllocationRunResponse {
  run_id: string;
  planning_week: number;
  initial_capital_deployed: number;
  new_capital_allocated: number;
  resulting_capital_deployed: number;
  budget_limit: number;
  capital_headroom: number;
  utilization_pct: number;
  total_units_allocated: number;
  total_expected_net_benefit: number;
  recommendations: AllocationRecommendation[];
}

export interface EOLActionOption {
  action: string;
  expected_cost: number;
  expected_recovery: number;
  net_financial_loss: number;
  units_affected: number;
  target_store_id?: string | null;
  assumptions: Record<string, any>;
  explanation: string;
}

export interface EOLRiskAssessment {
  assessment_id: string;
  store_id: string;
  product_id: string;
  product_name: string;
  lifecycle_stage: string;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  inventory_units: number;
  inventory_value: number;
  weeks_of_cover: number;
  successor_id?: string | null;
  successor_confidence?: number | null;
  weeks_to_successor?: number | null;
  weeks_to_eol?: number | null;
  risk_factors: Record<string, any>;
  markdown_option: EOLActionOption;
  transfer_option: EOLActionOption;
  hold_option: EOLActionOption;
  recommended_action: 'HOLD' | 'MARKDOWN' | 'TRANSFER' | 'NO_ACTION';
  expected_financial_impact: number;
  explanation: string;
}

export interface EOLTransferRoute {
  source_store_id: string;
  destination_store_id: string;
  product_id: string;
  requested_units: number;
  approved_units: number;
  source_excess_units: number;
  destination_shortfall_units: number;
  expected_cost: number;
  expected_loss: number;
  savings_vs_hold: number;
  status: string;
  rejection_reason?: string | null;
}

export interface PortfolioTransferResolution {
  approved_routes: EOLTransferRoute[];
  rejected_routes: EOLTransferRoute[];
  candidate_transfer_opportunity: number;
  approved_transfer_opportunity: number;
  source_capacity_ledger: Record<string, any>;
  destination_capacity_ledger: Record<string, any>;
}

export interface EOLRiskPortfolioResponse {
  current_week: number;
  min_risk_level: string;
  assessments_count: number;
  assessments: EOLRiskAssessment[];
  portfolio_resolution: PortfolioTransferResolution;
}

export interface SimulationConfig {
  start_week: number;
  end_week: number;
  capital_budget_limit?: number;
  starting_capital_target?: number;
  warehouse_cover_weeks?: number;
  baseline_lookback_weeks?: number;
}

export interface StartingInventorySnapshot {
  raw_inventory_cost: number;
  operational_inventory_cost: number;
  raw_total_units: number;
  operational_total_units: number;
  units_retained: number;
  units_removed: number;
  capital_headroom: number;
  methodology: string;
}

export interface WeeklySimulationResult {
  week_number: number;
  strategy_name: string;
  starting_store_units: number;
  starting_store_cost: number;
  ending_store_units: number;
  ending_store_cost: number;
  warehouse_units: number;
  warehouse_cost: number;
  units_allocated: number;
  allocation_cost: number;
  transferred_units: number;
  transfer_cost: number;
  markdowned_units: number;
  markdown_loss: number;
  demand_units: number;
  fulfilled_units: number;
  lost_sales_units: number;
  lost_sales_value: number;
  stockout_observations: number;
  positive_demand_observations: number;
  revenue: number;
  gross_margin: number;
  cogs: number;
  dead_stock_units: number;
  average_weeks_of_cover: number;
}

export interface SimulationRunResult {
  strategy_name: string;
  starting_snapshot: StartingInventorySnapshot;
  weekly_results?: WeeklySimulationResult[];
  stockout_rate: number;
  average_weeks_of_cover: number;
  dead_stock_pct: number;
  actual_markdown_loss: number;
  capital_turns: number;
  total_revenue: number;
  total_gross_margin: number;
  total_cogs: number;
  total_fulfilled_units: number;
  total_lost_sales_units: number;
  total_lost_sales_value: number;
  total_transferred_units: number;
  total_transfer_cost: number;
  total_allocated_units: number;
  total_allocation_cost: number;
  total_markdowned_units: number;
  average_inventory_cost: number;
  ending_inventory_cost: number;
  service_level_pct: number;
  runtime_seconds: number;
}

export interface MetricResult {
  metric_name: string;
  baseline_value: number;
  mobimart_value: number;
  absolute_difference: number;
  percentage_difference: number;
  unit: string;
}

export interface BenchmarkResponse {
  baseline: SimulationRunResult;
  mobimart: SimulationRunResult;
  metrics: Record<string, MetricResult>;
  summary_text: string;
}

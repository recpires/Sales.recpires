export type DiscountType = 'percentage' | 'fixed';

export interface Coupon {
  id: number;
  code: string;
  description: string;
  discount_type: DiscountType;
  discount_value: string;
  min_purchase_amount: string;
  max_discount_amount: string | null;
  usage_limit: number | null;
  usage_count: number;
  valid_from: string;
  valid_until: string;
  is_active: boolean;
  is_valid_now: boolean;
  valid_message: string;
  created_at: string;
  updated_at: string;
}

export interface CouponValidationRequest {
  code: string;
  total: number;
}

export interface CouponValidationResponse {
  valid: boolean;
  coupon: Coupon;
  discount: number;
  final_total: number;
}

export interface CouponCreateInput {
  code: string;
  description?: string;
  discount_type: DiscountType;
  discount_value: number | string;
  min_purchase_amount?: number | string;
  max_discount_amount?: number | string;
  usage_limit?: number;
  valid_from: string;
  valid_until: string;
  is_active?: boolean;
}

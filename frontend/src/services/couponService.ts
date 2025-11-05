import api from "./api";
import {
  Coupon,
  CouponValidationResponse,
  CouponCreateInput,
} from "../types/coupon";

export interface CouponListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Coupon[];
}

class CouponService {
  /**
   * Get all coupons
   */
  async getCoupons(): Promise<CouponListResponse> {
    const response = await api.get<CouponListResponse>("/coupons/");
    return response.data;
  }

  /**
   * Get single coupon
   */
  async getCoupon(id: number): Promise<Coupon> {
    const response = await api.get<Coupon>(`/coupons/${id}/`);
    return response.data;
  }

  /**
   * Validate coupon code
   */
  async validateCoupon(
    code: string,
    total: number
  ): Promise<CouponValidationResponse> {
    const response = await api.post<CouponValidationResponse>(
      "/coupons/validate_coupon/",
      { code, total }
    );
    return response.data;
  }

  /**
   * Create coupon (admin only)
   */
  async createCoupon(data: CouponCreateInput): Promise<Coupon> {
    const response = await api.post<Coupon>("/coupons/", data);
    return response.data;
  }

  /**
   * Update coupon (admin only)
   */
  async updateCoupon(
    id: number,
    data: Partial<CouponCreateInput>
  ): Promise<Coupon> {
    const response = await api.patch<Coupon>(`/coupons/${id}/`, data);
    return response.data;
  }

  /**
   * Delete coupon (admin only)
   */
  async deleteCoupon(id: number): Promise<void> {
    await api.delete(`/coupons/${id}/`);
  }
}

export default new CouponService();

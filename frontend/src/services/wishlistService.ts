import api from "./api";
import { Wishlist, WishlistToggleResponse } from "../types/wishlist";

export interface WishlistListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Wishlist[];
}

class WishlistService {
  /**
   * Get user's wishlist
   */
  async getWishlist(): Promise<WishlistListResponse> {
    const response = await api.get<WishlistListResponse>("/wishlist/");
    return response.data;
  }

  /**
   * Add product to wishlist
   */
  async addToWishlist(productId: number): Promise<Wishlist> {
    const response = await api.post<Wishlist>("/wishlist/", {
      product: productId,
    });
    return response.data;
  }

  /**
   * Remove product from wishlist
   */
  async removeFromWishlist(id: number): Promise<void> {
    await api.delete(`/wishlist/${id}/`);
  }

  /**
   * Toggle product in wishlist (add if not exists, remove if exists)
   */
  async toggleWishlist(productId: number): Promise<WishlistToggleResponse> {
    const response = await api.post<WishlistToggleResponse>(
      "/wishlist/toggle/",
      { product_id: productId }
    );
    return response.data;
  }

  /**
   * Check if product is in wishlist
   */
  async isInWishlist(productId: number): Promise<boolean> {
    try {
      const wishlist = await this.getWishlist();
      return wishlist.results.some((item) => item.product === productId);
    } catch (error) {
      return false;
    }
  }
}

export default new WishlistService();

import api from './api';
import { Review, ReviewCreateInput } from '../types/review';

export interface ReviewListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Review[];
}

class ReviewService {
  /**
   * Get all reviews (optionally filtered by product)
   */
  async getReviews(productId?: number): Promise<ReviewListResponse> {
    const params = productId ? { product: productId } : {};
    const response = await api.get<ReviewListResponse>('/reviews/', { params });
    return response.data;
  }

  /**
   * Get single review
   */
  async getReview(id: number): Promise<Review> {
    const response = await api.get<Review>(`/reviews/${id}/`);
    return response.data;
  }

  /**
   * Create review
   */
  async createReview(data: ReviewCreateInput): Promise<Review> {
    const response = await api.post<Review>('/reviews/', data);
    return response.data;
  }

  /**
   * Update review
   */
  async updateReview(id: number, data: Partial<ReviewCreateInput>): Promise<Review> {
    const response = await api.patch<Review>(`/reviews/${id}/`, data);
    return response.data;
  }

  /**
   * Delete review
   */
  async deleteReview(id: number): Promise<void> {
    await api.delete(`/reviews/${id}/`);
  }
}

export default new ReviewService();

import api from './api';
import { Category } from '../types/product';
import { Product } from '../types/product';

export interface CategoryListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Category[];
}

class CategoryService {
  /**
   * Get all categories
   */
  async getCategories(): Promise<CategoryListResponse> {
    const response = await api.get<CategoryListResponse>('/categories/');
    return response.data;
  }

  /**
   * Get single category by slug
   */
  async getCategory(slug: string): Promise<Category> {
    const response = await api.get<Category>(`/categories/${slug}/`);
    return response.data;
  }

  /**
   * Get products in a category
   */
  async getCategoryProducts(slug: string, params?: { min_price?: number; max_price?: number }): Promise<Product[]> {
    const response = await api.get<Product[]>(`/categories/${slug}/products/`, { params });
    return response.data;
  }

  /**
   * Create category (admin only)
   */
  async createCategory(data: Partial<Category>): Promise<Category> {
    const response = await api.post<Category>('/categories/', data);
    return response.data;
  }

  /**
   * Update category (admin only)
   */
  async updateCategory(slug: string, data: Partial<Category>): Promise<Category> {
    const response = await api.patch<Category>(`/categories/${slug}/`, data);
    return response.data;
  }

  /**
   * Delete category (admin only)
   */
  async deleteCategory(slug: string): Promise<void> {
    await api.delete(`/categories/${slug}/`);
  }
}

export default new CategoryService();

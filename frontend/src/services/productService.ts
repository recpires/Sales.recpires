import api from './api';

export interface Product {
  id: number;
  name: string;
  description: string;
  price: string;
  stock: number;
  category: string;
  sku: string;
  created_at: string;
  updated_at: string;
}

export interface ProductListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Product[];
}

class ProductService {
  /**
   * Get all products
   */
  async getProducts(): Promise<ProductListResponse> {
    const response = await api.get<ProductListResponse>('/products/');
    return response.data;
  }

  /**
   * Get single product
   */
  async getProduct(id: number): Promise<Product> {
    const response = await api.get<Product>(`/products/${id}/`);
    return response.data;
  }

  /**
   * Create product
   */
  async createProduct(data: Omit<Product, 'id' | 'created_at' | 'updated_at'>): Promise<Product> {
    const response = await api.post<Product>('/products/', data);
    return response.data;
  }

  /**
   * Update product
   */
  async updateProduct(id: number, data: Partial<Product>): Promise<Product> {
    const response = await api.patch<Product>(`/products/${id}/`, data);
    return response.data;
  }

  /**
   * Delete product
   */
  async deleteProduct(id: number): Promise<void> {
    await api.delete(`/products/${id}/`);
  }
}

export default new ProductService();
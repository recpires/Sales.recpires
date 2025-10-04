import api from './api';
import { Product, ProductCreateInput, ProductCreateInputWithoutImage } from '../types/product';

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
  async createProduct(data: ProductCreateInput): Promise<Product> {
    const response = await api.post<Product>('/products/', data);
    return response.data;
  }

  /**
   * Create product with image
   */
  async createProductWithImage(data: ProductCreateInputWithoutImage, image?: File): Promise<Product> {
    const formData = new FormData();

    Object.entries(data).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        formData.append(key, value.toString());
      }
    });

    if (image) {
      formData.append('image', image);
    }

    const response = await api.post<Product>('/products/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
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
   * Update product with image
   */
  async updateProductWithImage(id: number, data: Partial<Omit<Product, 'image'>>, image?: File): Promise<Product> {
    const formData = new FormData();

    Object.entries(data).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        formData.append(key, value.toString());
      }
    });

    if (image) {
      formData.append('image', image);
    }

    const response = await api.patch<Product>(`/products/${id}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
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
import api from './api';

export interface Store {
  id: number;
  name: string;
  description: string;
  phone: string;
  email: string;
  address: string;
  is_active: boolean;
  owner: number;
  owner_username: string;
  created_at: string;
  updated_at: string;
}

export interface StoreCreateData {
  name: string;
  description?: string;
  phone?: string;
  email?: string;
  address?: string;
}

export interface StoreUpdateData {
  name?: string;
  description?: string;
  phone?: string;
  email?: string;
  address?: string;
  is_active?: boolean;
}

const storeService = {
  /**
   * Get current user's store
   */
  async getMyStore(): Promise<Store> {
    const response = await api.get<Store>('/stores/my_store/');
    return response.data;
  },

  /**
   * Create a new store for the current user
   */
  async createStore(data: StoreCreateData): Promise<Store> {
    const response = await api.post<Store>('/stores/', data);
    return response.data;
  },

  /**
   * Update current user's store
   */
  async updateStore(id: number, data: StoreUpdateData): Promise<Store> {
    const response = await api.patch<Store>(`/stores/${id}/`, data);
    return response.data;
  },

  /**
   * Delete current user's store
   */
  async deleteStore(id: number): Promise<void> {
    await api.delete(`/stores/${id}/`);
  },

  /**
   * Check if user has a store
   */
  async hasStore(): Promise<boolean> {
    try {
      await this.getMyStore();
      return true;
    } catch (error) {
      return false;
    }
  },
};

export default storeService;

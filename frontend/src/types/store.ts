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

export interface StoreCreateInput {
  name: string;
  description?: string;
  phone?: string;
  email?: string;
  address?: string;
}

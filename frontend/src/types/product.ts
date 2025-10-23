export interface ProductVariant {
  id: number;
  product: number;
  name: string;
  sku: string;
  price: number;
  stock: number;
  created_at?: string;
  updated_at?: string;
}

export interface Product {
  id: number;
  name: string;
  description: string;
  image?: string;
  price?: number;
  sku: string;
  stock?: number;
  category: string;
  store: number;
  created_at?: string;
  updated_at?: string;
  variants?: ProductVariant[];
}

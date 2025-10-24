export interface ProductVariant {
  id: number;
  product: number;
  name: string;
  sku: string;
  price: number;
  stock: number;
  created_at?: string;
  updated_at?: string;
  is_active: boolean;
  image: string | null;
  created_at: string;
  updated_at: string;
  variants?: ProductVariant[];
  average_rating?: number;
  review_count?: number;
  categories?: Category[];
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

export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  image: string | null;
  parent: number | null;
  is_active: boolean;
  children?: Category[];
  product_count?: number;
  created_at: string;
  updated_at: string;
}

export type ColorChoice = 'red' | 'blue' | 'green' | 'black' | 'white' | 'yellow' | 'pink' | 'purple' | 'orange' | 'gray';
export type SizeChoice = 'XS' | 'S' | 'M' | 'L' | 'XL' | 'XXL';

export type ProductCreateInput = Omit<Product, 'id' | 'created_at' | 'updated_at' | 'color_display' | 'size_display' | 'store' | 'store_name' | 'seller_name' | 'average_rating' | 'review_count' | 'categories'>;
export type ProductCreateInputWithoutImage = Omit<Product, 'id' | 'created_at' | 'updated_at' | 'color_display' | 'size_display' | 'store' | 'store_name' | 'seller_name' | 'image' | 'average_rating' | 'review_count' | 'categories'>;

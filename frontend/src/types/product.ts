export interface Product {
  id: number;
  store: number | null;
  store_name: string;
  seller_name: string;
  name: string;
  description: string;
  price: string;
  color: string;
  color_display: string;
  size: string;
  size_display: string;
  stock: number;
  sku: string;
  is_active: boolean;
  image: string | null;
  created_at: string;
  updated_at: string;
  variants?: ProductVariant[];
  average_rating?: number;
  review_count?: number;
  categories?: Category[];
}

export interface ProductVariant {
  id: number;
  sku: string;
  price: string;
  color?: string | null;
  size?: string | null;
  stock: number;
  image?: string | null;
  is_active?: boolean;
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

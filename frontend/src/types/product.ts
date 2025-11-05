// Types for products and variants used in the frontend UI

export interface Category {
  id: number;
  name: string;
  slug?: string;
  description?: string;
  image?: string | null;
  parent?: number | null;
  is_active?: boolean;
  children?: Category[];
  product_count?: number;
  created_at?: string;
  updated_at?: string;
}

export interface ProductVariant {
  id: number;
  product: number;
  name?: string;
  sku?: string;
  price?: number;
  stock?: number;
  is_active?: boolean;
  image?: string | null;
  // Optional display attributes
  size?: string;
  color?: string;
  created_at?: string;
  updated_at?: string;
  average_rating?: number;
  review_count?: number;
  categories?: Category[];
}

export interface Product {
  id: number;
  name?: string;
  description?: string;
  image?: string | null;
  price?: number;
  sku?: string;
  stock?: number;
  category?: string | number;
  store?: number;
  // Optional fields used across the UI
  store_name?: string;
  seller_name?: string;
  average_rating?: number;
  review_count?: number;
  color?: string;
  size?: string;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
  variants?: ProductVariant[];
}

export type ColorChoice =
  | "red"
  | "blue"
  | "green"
  | "black"
  | "white"
  | "yellow"
  | "pink"
  | "purple"
  | "orange"
  | "gray";

export type SizeChoice = "XS" | "S" | "M" | "L" | "XL" | "XXL";

export type ProductCreateInput = Omit<
  Product,
  | "id"
  | "created_at"
  | "updated_at"
  | "store_name"
  | "seller_name"
  | "average_rating"
  | "review_count"
  | "variants"
>;

export type ProductCreateInputWithoutImage = Omit<
  Product,
  | "id"
  | "created_at"
  | "updated_at"
  | "store_name"
  | "seller_name"
  | "image"
  | "average_rating"
  | "review_count"
  | "variants"
>;

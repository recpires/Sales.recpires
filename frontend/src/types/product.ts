export interface Product {
  id: number;
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
  created_at: string;
  updated_at: string;
}

export type ColorChoice = 'red' | 'blue' | 'green' | 'black' | 'white' | 'yellow' | 'pink' | 'purple' | 'orange' | 'gray';
export type SizeChoice = 'XS' | 'S' | 'M' | 'L' | 'XL' | 'XXL';

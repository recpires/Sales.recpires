import { Product } from './product';

export interface Wishlist {
  id: number;
  user: number;
  product: number;
  product_details?: Product;
  created_at: string;
}

export interface WishlistToggleRequest {
  product_id: number;
}

export interface WishlistToggleResponse {
  action: 'added' | 'removed';
  message: string;
  wishlist?: Wishlist;
}

export interface Review {
  id: number;
  product: number;
  user: number;
  user_name: string;
  user_first_name: string;
  rating: number;
  title: string;
  comment: string;
  is_verified_purchase: boolean;
  is_approved: boolean;
  created_at: string;
  updated_at: string;
}

export interface ReviewCreateInput {
  product: number;
  rating: number;
  title?: string;
  comment?: string;
}

export interface ReviewStats {
  average_rating: number;
  total_reviews: number;
  rating_distribution: {
    [key: number]: number;
  };
}

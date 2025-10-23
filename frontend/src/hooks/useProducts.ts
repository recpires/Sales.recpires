import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';
import { Product } from '../types/product';

interface ProductsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Product[];
}

/**
 * Hook to fetch all products
 */
export const useProducts = () => {
  return useQuery<ProductsResponse>({
    queryKey: ['products'],
    queryFn: async () => {
      const response = await api.get('/products/');
      return response.data;
    },
  });
};

/**
 * Hook to create a new product with image
 */
export const useCreateProductWithImage = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ data, image }: { data: any; image?: File }) => {
      const formData = new FormData();

      // Append product data (excluding variants for FormData)
      const { variants, ...productData } = data;
      Object.keys(productData).forEach((key) => {
        if (productData[key] !== undefined && productData[key] !== null) {
          formData.append(key, productData[key]);
        }
      });

      // Append variants as JSON if present
      if (variants && Array.isArray(variants) && variants.length > 0) {
        formData.append('variants', JSON.stringify(variants));
      }

      // Append image if provided
      if (image) {
        formData.append('image', image);
      }

      const response = await api.post('/products/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
    },
  });
};

/**
 * Hook to delete a product
 */
export const useDeleteProduct = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (productId: number) => {
      await api.delete(`/products/${productId}/`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
    },
  });
};

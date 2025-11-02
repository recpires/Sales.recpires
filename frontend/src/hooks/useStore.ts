import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import storeService, {
  StoreCreateData,
  StoreUpdateData,
} from "../services/storeService";

/**
 * Hook to fetch current user's store
 */
export const useMyStore = () => {
  return useQuery({
    queryKey: ["myStore"],
    queryFn: () => storeService.getMyStore(),
    retry: false, // Don't retry if user doesn't have a store (404)
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook to create a new store
 */
export const useCreateStore = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: StoreCreateData) => storeService.createStore(data),
    onSuccess: (newStore) => {
      queryClient.setQueryData(["myStore"], newStore);
      queryClient.invalidateQueries({ queryKey: ["myStore"] });
    },
  });
};

/**
 * Hook to update store
 */
export const useUpdateStore = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: StoreUpdateData }) =>
      storeService.updateStore(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["myStore"] });
    },
  });
};

/**
 * Hook to delete store
 */
export const useDeleteStore = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => storeService.deleteStore(id),
    onSuccess: () => {
      queryClient.setQueryData(["myStore"], null);
      queryClient.invalidateQueries({ queryKey: ["myStore"] });
    },
  });
};

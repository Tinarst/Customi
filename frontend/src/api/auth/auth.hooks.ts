import { registerRequest, requestOtp, verifyOtp } from "./auth.api";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { MY_USER_KEY } from "@/api/myuser/myuser.hooks";
import { MutationOptionsFromFn } from "@/types";

// Login hook
export function useRequestOtp(
  options?: MutationOptionsFromFn<typeof requestOtp>,
) {
  const queryClient = useQueryClient();
  return useMutation({
    ...options,
    mutationFn: requestOtp,
    onSettled(...args) {
      queryClient.invalidateQueries({ queryKey: [MY_USER_KEY] });
      options?.onSettled?.(...args);
    },
  });
}

// Register hook
export function useVerifyOtp(
  options?: MutationOptionsFromFn<typeof verifyOtp>,
) {
  const queryClient = useQueryClient();
  return useMutation({
    ...options,
    mutationFn: verifyOtp,
    onSettled(...args) {
      queryClient.invalidateQueries({ queryKey: [MY_USER_KEY] });
      options?.onSettled?.(...args);
    },
  });
}

export function useRegister(
  options?: MutationOptionsFromFn<typeof registerRequest>,
) {
  const queryClient = useQueryClient();
  return useMutation({
    ...options,
    mutationFn: registerRequest,
    onSettled(...args) {
      queryClient.invalidateQueries({ queryKey: [MY_USER_KEY] });
      options?.onSettled?.(...args);
    },
  });
}

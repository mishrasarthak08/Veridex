import { useState } from "react"
import { toast } from "sonner"

interface OptimisticMutationOptions<TData, TVariables> {
  mutationFn: (variables: TVariables) => Promise<TData>
  onMutate?: (variables: TVariables) => any | Promise<any>
  onSuccess?: (data: TData, variables: TVariables, context: any) => void
  onError?: (error: any, variables: TVariables, context: any) => void
  successMessage?: string
}

/**
 * A simplified optimistic mutation hook.
 * For production, consider using TanStack Query's useMutation.
 */
export function useOptimisticMutation<TData, TVariables>({
  mutationFn,
  onMutate,
  onSuccess,
  onError,
  successMessage
}: OptimisticMutationOptions<TData, TVariables>) {
  const [isLoading, setIsLoading] = useState(false)

  const mutate = async (variables: TVariables) => {
    setIsLoading(true)
    let context: any
    
    // 1. Optimistic update
    if (onMutate) {
      context = await onMutate(variables)
    }

    try {
      // 2. Server execution
      const data = await mutationFn(variables)
      
      // 3. Confirm success
      if (successMessage) toast.success(successMessage)
      if (onSuccess) onSuccess(data, variables, context)
      
      return data
    } catch (error: any) {
      // 4. Rollback and error
      // Note: The global interceptor already handles the error toast
      if (onError) onError(error, variables, context)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  return { mutate, isLoading }
}

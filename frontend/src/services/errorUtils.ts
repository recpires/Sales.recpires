export function getApiErrors(error: any): any {
  // axios error object with normalized apiErrors (set by api.ts interceptor)
  if (!error) return null;
  if (error.apiErrors) return error.apiErrors;
  if (error.response && error.response.data) return error.response.data;
  if (error.message) return { detail: error.message };
  return null;
}

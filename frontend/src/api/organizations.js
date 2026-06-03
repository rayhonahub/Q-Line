import api from "./axios"

export const orgsAPI = {
  getPublic:   ()         => api.get("/orgs/public/"),
  getBranches: (orgId)    => api.get(`/orgs/${orgId}/branches/public/`),
  getQueues:   (branchId) => api.get(`/queues/branches/${branchId}/queues/`),
}
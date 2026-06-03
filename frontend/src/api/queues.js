import api from "./axios"

export const queuesAPI = {
  createTicket: (queueId) => api.post("/queues/tickets/create/", { queue: queueId }),
  myTickets:    ()        => api.get("/queues/tickets/my/"),
  cancel:       (id)      => api.post(`/queues/tickets/${id}/cancel/`),
  rate:         (id, rating) => api.patch(`/queues/tickets/${id}/rating/`, { rating }),
}
import { request } from './apiClient';

const TEAMS_PATH = '/api/teams-service';

export const teamsApi = {
  list: (search = '') =>
    request(search ? `${TEAMS_PATH}?search=${encodeURIComponent(search)}` : TEAMS_PATH),
  create: (team) => request(TEAMS_PATH, { method: 'POST', body: team }),
  update: (id, team) => request(`${TEAMS_PATH}/${id}`, { method: 'PUT', body: team }),
  remove: (id) => request(`${TEAMS_PATH}/${id}`, { method: 'DELETE' }),
};

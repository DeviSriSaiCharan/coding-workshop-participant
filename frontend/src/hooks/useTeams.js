import { useCallback, useEffect, useState } from 'react';
import { teamsApi } from '../services/teamsApi';

// Owns the teams list state and exposes CRUD actions that keep it in sync.
export function useTeams(search) {
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      setTeams(await teamsApi.list(search));
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const saveTeam = useCallback(
    async (team, id) => {
      await (id ? teamsApi.update(id, team) : teamsApi.create(team));
      await refresh();
    },
    [refresh],
  );

  const deleteTeam = useCallback(
    async (id) => {
      await teamsApi.remove(id);
      await refresh();
    },
    [refresh],
  );

  return { teams, loading, error, saveTeam, deleteTeam };
}

import { useState } from 'react';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import TeamFormDialog from '../components/TeamFormDialog';
import TeamList from '../components/TeamList';
import { useDebouncedValue } from '../hooks/useDebouncedValue';
import { useTeams } from '../hooks/useTeams';

export default function TeamsPage() {
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebouncedValue(search);
  const { teams, loading, error, saveTeam, deleteTeam } = useTeams(debouncedSearch);

  const [dialog, setDialog] = useState({ open: false, team: null, key: 0 });
  const openDialog = (team = null) => setDialog((d) => ({ open: true, team, key: d.key + 1 }));
  const closeDialog = () => setDialog((d) => ({ ...d, open: false }));

  const [actionError, setActionError] = useState('');
  const handleDelete = async (team) => {
    if (!window.confirm(`Delete team "${team.name}"?`)) return;
    try {
      await deleteTeam(team.id);
      setActionError('');
    } catch (err) {
      setActionError(err.message);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Stack
        direction={{ xs: 'column', sm: 'row' }}
        spacing={2}
        sx={{ mb: 3, justifyContent: 'space-between', alignItems: { sm: 'center' } }}
      >
        <Typography variant="h4" component="h1">
          Teams
        </Typography>
        <Stack direction="row" spacing={2}>
          <TextField
            size="small"
            label="Search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
          <Button variant="contained" onClick={() => openDialog()}>
            New team
          </Button>
        </Stack>
      </Stack>

      {(error || actionError) && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error || actionError}
        </Alert>
      )}

      {loading && teams.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
          <CircularProgress />
        </Box>
      ) : (
        <TeamList teams={teams} onEdit={openDialog} onDelete={handleDelete} />
      )}

      <TeamFormDialog
        key={dialog.key}
        open={dialog.open}
        team={dialog.team}
        onClose={closeDialog}
        onSave={saveTeam}
      />
    </Container>
  );
}

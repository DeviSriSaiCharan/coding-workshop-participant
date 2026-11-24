import { useState } from 'react';
import {
  Alert,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Stack,
  TextField,
} from '@mui/material';

const EMPTY_TEAM = { name: '', location: '', leader: '' };

// Parent remounts this dialog (via `key`) for each open, so initial state is always fresh.
export default function TeamFormDialog({ open, team, onClose, onSave }) {
  const [values, setValues] = useState(() => pickFields(team));
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const isEdit = Boolean(team?.id);
  const handleChange = (field) => (event) =>
    setValues((current) => ({ ...current, [field]: event.target.value }));

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!values.name.trim()) {
      setError('Team name is required');
      return;
    }
    setSaving(true);
    try {
      await onSave(values, team?.id);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <form onSubmit={handleSubmit} noValidate>
        <DialogTitle>{isEdit ? 'Edit team' : 'New team'}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            {error && <Alert severity="error">{error}</Alert>}
            <TextField label="Name" value={values.name} onChange={handleChange('name')} required autoFocus />
            <TextField label="Location" value={values.location} onChange={handleChange('location')} />
            <TextField label="Team leader" value={values.leader} onChange={handleChange('leader')} />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button type="submit" variant="contained" disabled={saving}>
            {saving ? 'Saving…' : 'Save'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}

function pickFields(team) {
  return {
    name: team?.name ?? EMPTY_TEAM.name,
    location: team?.location ?? EMPTY_TEAM.location,
    leader: team?.leader ?? EMPTY_TEAM.leader,
  };
}

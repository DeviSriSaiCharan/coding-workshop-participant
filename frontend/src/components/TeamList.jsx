import {
  Button,
  Card,
  CardActions,
  CardContent,
  Grid,
  Typography,
} from '@mui/material';

export default function TeamList({ teams, onEdit, onDelete }) {
  if (teams.length === 0) {
    return (
      <Typography color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
        No teams yet. Create the first one.
      </Typography>
    );
  }

  return (
    <Grid container spacing={2}>
      {teams.map((team) => (
        <Grid key={team.id} size={{ xs: 12, sm: 6, md: 4 }}>
          <TeamCard team={team} onEdit={onEdit} onDelete={onDelete} />
        </Grid>
      ))}
    </Grid>
  );
}

function TeamCard({ team, onEdit, onDelete }) {
  return (
    <Card variant="outlined" sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Typography variant="h6" component="h2" gutterBottom>
          {team.name}
        </Typography>
        <Detail label="Location" value={team.location} />
        <Detail label="Leader" value={team.leader} />
      </CardContent>
      <CardActions>
        <Button size="small" onClick={() => onEdit(team)}>
          Edit
        </Button>
        <Button size="small" color="error" onClick={() => onDelete(team)}>
          Delete
        </Button>
      </CardActions>
    </Card>
  );
}

function Detail({ label, value }) {
  return (
    <Typography variant="body2" color="text.secondary">
      {label}: {value || '—'}
    </Typography>
  );
}

import { AppBar, CssBaseline, ThemeProvider, Toolbar, Typography, createTheme } from '@mui/material';
import TeamsPage from './pages/TeamsPage';

const theme = createTheme({
  palette: { primary: { main: '#1565c0' } },
});

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="static" elevation={0}>
        <Toolbar>
          <Typography variant="h6" component="div">
            Team Management
          </Typography>
        </Toolbar>
      </AppBar>
      <TeamsPage />
    </ThemeProvider>
  );
}

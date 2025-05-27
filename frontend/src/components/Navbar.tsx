import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Container,
} from '@mui/material';
import ShowChartIcon from '@mui/icons-material/ShowChart';

const Navbar = () => {
  return (
    <AppBar position="static">
      <Container maxWidth="lg">
        <Toolbar>
          <img 
            src="/yonsei-logo.svg" 
            alt="Yonsei University" 
            style={{ 
              width: '40px', 
              height: '40px', 
              marginRight: '16px',
              backgroundColor: 'white',
              borderRadius: '50%',
              padding: '4px'
            }} 
          />
          <Typography
            variant="h6"
            component={RouterLink}
            to="https://fintech.yonsei.ac.kr/"
            sx={{
              flexGrow: 1,
              textDecoration: 'none',
              color: 'inherit',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            LPPL AI DASHBOARD
          </Typography>
          <Button
            color="inherit"
            component={RouterLink}
            to="http://ahn.yonsei.ac.kr/"
          >
            QFL
          </Button>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Navbar;

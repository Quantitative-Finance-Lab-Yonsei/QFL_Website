import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  CircularProgress,
  Paper,
  Grid,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import axios from 'axios';

interface StockData {
  date: string;
  open_price: number;
  high_price: number;
  low_price: number;
  close_price: number;
  volume: number;
}

interface Company {
  id: number;
  symbol: string;
  name: string;
  sector: string;
  industry: string;
}

const CompanyDetail = () => {
  const { symbol } = useParams<{ symbol: string }>();
  const [company, setCompany] = useState<Company | null>(null);
  const [stockData, setStockData] = useState<StockData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [companyResponse, stockDataResponse] = await Promise.all([
          axios.get(`http://localhost:8000/api/v1/companies/symbol/${symbol}`),
          axios.get(`http://localhost:8000/api/v1/stock_data/${symbol}`),
        ]);
        setCompany(companyResponse.data);
        setStockData(stockDataResponse.data);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [symbol]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (!company) {
    return (
      <Container>
        <Typography variant="h5" color="error">
          Company not found
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom>
          {company.name} ({company.symbol})
        </Typography>
        <Typography variant="subtitle1" color="textSecondary" gutterBottom>
          {company.sector} - {company.industry}
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Stock Price History
            </Typography>
            <Box height={400}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={stockData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="close_price"
                    stroke="#1976d2"
                    name="Close Price"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Latest Stock Data
            </Typography>
            {stockData.length > 0 && (
              <Box>
                <Typography>
                  Date: {stockData[0].date}
                </Typography>
                <Typography>
                  Open: ${stockData[0].open_price.toFixed(2)}
                </Typography>
                <Typography>
                  High: ${stockData[0].high_price.toFixed(2)}
                </Typography>
                <Typography>
                  Low: ${stockData[0].low_price.toFixed(2)}
                </Typography>
                <Typography>
                  Close: ${stockData[0].close_price.toFixed(2)}
                </Typography>
                <Typography>
                  Volume: {stockData[0].volume.toLocaleString()}
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default CompanyDetail; 
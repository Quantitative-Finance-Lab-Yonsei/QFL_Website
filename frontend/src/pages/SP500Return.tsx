import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  ReferenceArea,
} from 'recharts';
import axios from 'axios';

const ASSETS = [
  { 
    key: 'sp500', 
    label: 'S&P 500', 
    endpoint: 'sp500-index', 
    color: 'rgb(75, 192, 192)',
    description: 'US Stock Market Index',
    img: '/sp500.svg'
  },
  { 
    key: 'gold', 
    label: 'Gold', 
    endpoint: 'gold-index', 
    color: 'rgb(255, 215, 0)',
    description: 'Gold Futures Price',
    img: '/gold.svg'
  },
  { 
    key: 'interest', 
    label: 'Interest Rate', 
    endpoint: 'interest-rate', 
    color: 'rgb(255, 0, 0)',
    description: '5-Year Treasury Yield',
    img: '/interest.svg'
  },
  { 
    key: 'bitcoin', 
    label: 'Bitcoin', 
    endpoint: 'bitcoin-index', 
    color: 'rgb(255, 165, 0)',
    description: 'Bitcoin USD Price',
    img: '/bitcoin.svg'
  },
  { 
    key: 'fx', 
    label: 'FX Rate', 
    endpoint: 'fx-rate', 
    color: 'rgb(0, 0, 255)',
    description: 'EUR/USD Exchange Rate',
    img: '/fx.svg'
  },
];

interface DataPoint {
  date: string;
  logPrice: number;
  dtcai: number;
}

interface ColorSegment {
  start: number;
  end: number;
  color: string;
}

const SP500Return = () => {
  const [selectedAsset, setSelectedAsset] = useState<typeof ASSETS[0] | null>(null);
  const [data, setData] = useState<DataPoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedAsset) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        const apiUrl = `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/v1/${selectedAsset.endpoint}/`;
        console.log('Attempting to fetch from:', apiUrl);
        
        const response = await axios.get(apiUrl, {
          params: { days: 3650 }
        });

        if (!response.data || !Array.isArray(response.data)) {
          throw new Error('Invalid response format from server');
        }

        const transformedData = response.data
          .map((item: any) => ({
            date: new Date(item.date).toISOString().split('T')[0],
            logPrice: item.close_price > 0 ? Math.log(item.close_price) : 0,
            dtcai: item.dtcai || 0,
          }))
          .filter(item => {
            const year = new Date(item.date).getFullYear();
            return year >= 2019 && year <= 2024;
          })
          .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

        setData(transformedData);
        setError(null);
      } catch (err) {
        console.error('Error fetching data:', err);
        if (axios.isAxiosError(err)) {
          setError(`Failed to load data: ${err.message}. Status: ${err.response?.status}`);
        } else {
          setError('Failed to load data. Please try again later.');
        }
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [selectedAsset]);

  const getColorForValue = (value: number) => {
    if (value < 0.3) return 'rgba(0, 255, 0, 0.5)'; // Brighter Green
    if (value < 0.6) return 'rgba(255, 165, 0, 0.5)'; // Brighter Orange
    return 'rgba(255, 0, 0, 0.5)'; // Brighter Red
  };

  const renderChart = () => {
    // Create color segments
    const segments: ColorSegment[] = [];
    let currentSegment: ColorSegment = {
      start: 0,
      end: 0,
      color: getColorForValue(data[0]?.dtcai || 0),
    };

    for (let i = 1; i < data.length; i++) {
      const currentColor = getColorForValue(data[i].dtcai);
      if (currentColor !== currentSegment.color) {
        segments.push({
          ...currentSegment,
          end: i - 1,
        });
        currentSegment = {
          start: i,
          end: i,
          color: currentColor,
        };
      }
    }
    segments.push({
      ...currentSegment,
      end: data.length - 1,
    });

    return (
      <div style={{ height: '600px', marginBottom: '2rem' }}>
        <h3 style={{ textAlign: 'center', marginBottom: '1rem', fontFamily: 'Times New Roman', fontSize: '20px' }}>
          S&P 500
        </h3>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <defs>
              <linearGradient id="colorGreen" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="rgba(0, 255, 0, 0.5)" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="rgba(0, 255, 0, 0.5)" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorOrange" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="rgba(255, 165, 0, 0.5)" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="rgba(255, 165, 0, 0.5)" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorRed" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="rgba(255, 0, 0, 0.5)" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="rgba(255, 0, 0, 0.5)" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="date" 
              tick={{ fontFamily: 'Times New Roman', fontSize: 16 }}
              tickFormatter={(value) => new Date(value).getFullYear().toString()}
              domain={['2019-01-01', '2024-12-31']}
            />
            <YAxis 
              tick={{ fontFamily: 'Times New Roman', fontSize: 16 }}
              label={{ 
                value: 'Log-price', 
                angle: -90, 
                position: 'insideLeft',
                style: { fontFamily: 'Times New Roman', fontSize: 16 }
              }}
            />
            <Tooltip />
            <Legend />
            {segments.map((segment, index) => (
              <ReferenceArea
                key={index}
                x1={data[segment.start].date}
                x2={data[segment.end].date}
                y1={0}
                y2={data[segment.start].logPrice}
                fill={segment.color}
                fillOpacity={0.5}
              />
            ))}
            <Line
              type="monotone"
              dataKey="logPrice"
              stroke="black"
              strokeWidth={1.3}
              name="S&P500"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginTop: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <div style={{ width: '20px', height: '20px', backgroundColor: 'rgba(255, 0, 0, 0.5)' }}></div>
            <span style={{ fontFamily: 'Times New Roman', fontSize: '16px' }}>crash-alert</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <div style={{ width: '20px', height: '20px', backgroundColor: 'rgba(255, 165, 0, 0.5)' }}></div>
            <span style={{ fontFamily: 'Times New Roman', fontSize: '16px' }}>caution</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <div style={{ width: '20px', height: '20px', backgroundColor: 'rgba(0, 255, 0, 0.5)' }}></div>
            <span style={{ fontFamily: 'Times New Roman', fontSize: '16px' }}>stable</span>
          </div>
        </div>
      </div>
    );
  };

  const handleBack = () => {
    setSelectedAsset(null);
    setData([]);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {!selectedAsset ? (
        <>
          <div style={{ width: '100%', height: '300px', marginBottom: '2rem', borderRadius: '0.75rem', overflow: 'hidden' }}>
            <img src="/yonsei_univ_photo.png" alt="Yonsei University" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'row', gap: '1.5rem', overflowX: 'auto', paddingBottom: '1rem' }}>
            {ASSETS.map(asset => (
              <div
                key={asset.key}
                onClick={() => setSelectedAsset(asset)}
                style={{ 
                  minWidth: '300px',
                  padding: '1.5rem',
                  borderRadius: '0.75rem',
                  cursor: 'pointer',
                  border: '4px solid #d1d5db',
                  backgroundColor: 'white',
                  transition: 'all 0.3s'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.borderColor = '#60a5fa';
                  e.currentTarget.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.borderColor = '#d1d5db';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <img 
                    src={asset.img} 
                    alt={asset.label}
                    style={{ 
                      width: '32px',
                      height: '32px',
                      objectFit: 'contain'
                    }}
                  />
                  <div>
                    <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#1f2937' }}>{asset.label}</h3>
                    <p style={{ fontSize: '0.875rem', color: '#4b5563' }}>{asset.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      ) : (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-800">{selectedAsset.label}</h2>
            <button
              onClick={handleBack}
              className="btn-gradient red block px-6 py-2 text-white font-medium rounded-lg transition-all duration-300 hover:shadow-lg"
              style={{
                background: 'linear-gradient(45deg, #1976d2, #42a5f5)',
                border: 'none',
                cursor: 'pointer'
              }}
            >
              ← Back to Assets
            </button>
          </div>
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
          ) : error ? (
            <div className="text-red-500 text-center">{error}</div>
          ) : !data.length ? (
            <div className="text-center">No data available</div>
          ) : (
            <div>
              {renderChart()}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SP500Return;

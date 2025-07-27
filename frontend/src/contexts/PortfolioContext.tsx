import React, { createContext, useState, useContext, useEffect, useRef } from 'react';
import { db } from '@/lib/firebase'; 
import { doc, getDoc, setDoc } from 'firebase/firestore';
import { useUser } from './UserContext';

interface PortfolioStock {
  symbol: string;
  name: string;
  quantity: number;
  avgPrice: number;
  currentPrice: number;
  change: number;
  percentChange: number;
}

interface PortfolioContextType {
  portfolio: PortfolioStock[];
  addToPortfolio: (stock: PortfolioStock) => void;
  removeFromPortfolio: (symbol: string) => void;
  updatePortfolio: (stocks: PortfolioStock[]) => void;
}

const PortfolioContext = createContext<PortfolioContextType>({
  portfolio: [],
  addToPortfolio: () => {},
  removeFromPortfolio: () => {},
  updatePortfolio: () => {}
});

export const usePortfolio = () => useContext(PortfolioContext);

export const PortfolioProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [portfolio, setPortfolio] = useState<PortfolioStock[]>([]);
  const [portfolioLoading, setPortfolioLoading] = useState(true);
  const { user } = useUser();
  const hasLoaded = useRef(false);

  // Load portfolio from Firestore or localStorage on mount or user change
  useEffect(() => {
    const loadPortfolio = async () => {
      setPortfolioLoading(true);
      if (user && user.uid) {
        const docRef = doc(db, 'portfolios', user.uid);
        const docSnap = await getDoc(docRef);
        setPortfolio(docSnap.exists() ? docSnap.data().stocks || [] : []);
      } else {
        const savedPortfolio = localStorage.getItem('portfolio');
        setPortfolio(savedPortfolio ? JSON.parse(savedPortfolio) : []);
      }
      setPortfolioLoading(false);
      hasLoaded.current = true;
    };
    loadPortfolio().catch(console.error);
    // eslint-disable-next-line
  }, [user]);

  // Save portfolio to Firestore or localStorage whenever it changes
  useEffect(() => {
    if (!hasLoaded.current || portfolioLoading) return;
    
    const savePortfolio = async () => {
      // Create a clean version of the portfolio for saving, replacing any NaN with 0.
      const cleanedPortfolio = portfolio.map(stock => ({
        ...stock,
        avgPrice: isNaN(stock.avgPrice) ? 0 : stock.avgPrice,
        quantity: isNaN(stock.quantity) ? 0 : stock.quantity,
      }));

      if (user && user.uid) {
        try {
          await setDoc(doc(db, 'portfolios', user.uid), { stocks: cleanedPortfolio }, { merge: true });
        } catch (error) {
          console.error("Firestore save failed!", error);
          console.log("Data that failed to save:", { stocks: cleanedPortfolio });
        }
      } else {
        localStorage.setItem('portfolio', JSON.stringify(cleanedPortfolio));
      }
    };
    savePortfolio();
  }, [portfolio, user, portfolioLoading]);

  const addToPortfolio = (stock: Partial<PortfolioStock>) => {
    // Sanitize the incoming stock data to prevent undefined/NaN issues
    const newStockData = {
      symbol: stock.symbol || '',
      name: stock.name || '',
      quantity: stock.quantity || 0,
      avgPrice: stock.avgPrice || 0,
      currentPrice: stock.currentPrice || 0,
      change: stock.change ?? 0, // Use ?? to allow negative numbers but block null/undefined
      percentChange: stock.percentChange ?? 0,
    };

    if (!newStockData.symbol) {
      console.error("Attempted to add a stock with no symbol.");
      return;
    }

    setPortfolio(current => {
      const existingStock = current.find(s => s.symbol === newStockData.symbol);

      if (existingStock) {
        return current.map(s => {
          if (s.symbol === newStockData.symbol) {
            const totalQuantity = (s.quantity || 0) + newStockData.quantity;
            
            // Guard against division by zero and NaN values
            const newAvgPrice = totalQuantity > 0 
              ? (((s.avgPrice || 0) * (s.quantity || 0)) + (newStockData.avgPrice * newStockData.quantity)) / totalQuantity
              : 0;

            return {
              ...s,
              quantity: totalQuantity,
              avgPrice: isNaN(newAvgPrice) ? 0 : newAvgPrice,
              currentPrice: newStockData.currentPrice,
              change: newStockData.change,
              percentChange: newStockData.percentChange,
            };
          }
          return s;
        });
      }
      // Add new sanitized stock
      return [...current, newStockData];
    });
  };

  const removeFromPortfolio = (symbol: string) => {
    setPortfolio(current => current.filter(stock => stock.symbol !== symbol));
  };

  const updatePortfolio = (stocks: PortfolioStock[]) => {
    setPortfolio(stocks);
  };

  return (
    <PortfolioContext.Provider value={{ portfolio, addToPortfolio, removeFromPortfolio, updatePortfolio }}>
      {children}
    </PortfolioContext.Provider>
  );
};

export default PortfolioContext;
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, LoadingSpinner, Button } from '../components';
import apiService from '../services/api';
import type { Watchlist } from '../types';

export const WatchlistsPage: React.FC = () => {
  const navigate = useNavigate();
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadWatchlists = async () => {
      try {
        setLoading(true);
        const data = await apiService.getWatchlists();
        setWatchlists(data);
      } catch (error) {
        console.error('Error loading watchlists:', error);
      } finally {
        setLoading(false);
      }
    };

    loadWatchlists();
  }, []);

  const handleDeleteWatchlist = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this watchlist?')) {
      try {
        await apiService.deleteWatchlist(id);
        setWatchlists(watchlists.filter((w) => w.id !== id));
      } catch (error) {
        console.error('Error deleting watchlist:', error);
      }
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold">Watchlists</h1>
          <Button onClick={() => navigate('/watchlists/new')} variant="primary">
            New Watchlist
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {watchlists.map((watchlist) => (
            <Card key={watchlist.id} className="flex flex-col">
              <h3 className="text-2xl font-bold mb-2">{watchlist.name}</h3>
              <p className="text-gray-600 mb-4 flex-grow">{watchlist.description}</p>
              <p className="text-sm text-gray-500 mb-4">
                {watchlist.entries?.length || 0} symbols
              </p>
              <div className={`mb-4 inline-block px-3 py-1 rounded text-white text-sm ${watchlist.is_active ? 'bg-green-600' : 'bg-gray-600'}`}>
                {watchlist.is_active ? 'Active' : 'Inactive'}
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={() => navigate(`/watchlists/${watchlist.id}`)}
                  variant="secondary"
                  className="flex-1"
                >
                  View
                </Button>
                <Button
                  onClick={() => navigate(`/watchlists/${watchlist.id}/edit`)}
                  variant="secondary"
                  className="flex-1"
                >
                  Edit
                </Button>
                <Button
                  onClick={() => handleDeleteWatchlist(watchlist.id)}
                  variant="danger"
                  className="flex-1"
                >
                  Delete
                </Button>
              </div>
            </Card>
          ))}
        </div>

        {watchlists.length === 0 && (
          <Card className="text-center py-12">
            <p className="text-gray-600 mb-4">No watchlists yet</p>
            <Button onClick={() => navigate('/watchlists/new')} variant="primary">
              Create your first watchlist
            </Button>
          </Card>
        )}
      </div>
    </div>
  );
};

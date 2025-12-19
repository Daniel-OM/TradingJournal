export function AssetsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">Assets / Screener</h1>
        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center gap-2 transition-colors">
          <i className="fas fa-refresh"></i>
          Refresh Data
        </button>
      </div>

      {/* Placeholder */}
      <div className="bg-slate-800 rounded-lg p-8 text-center">
        <i className="fas fa-chart-line text-4xl text-slate-600 mb-4"></i>
        <h2 className="text-xl font-bold text-white mb-2">Assets Page</h2>
        <p className="text-slate-400">Coming soon - Stock screener and asset tracking</p>
      </div>
    </div>
  );
}

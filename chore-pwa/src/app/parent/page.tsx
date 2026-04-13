"use client";

import { useState, useEffect } from "react";
import { supabase } from "@/utils/supabase/client";
import { ListTodo, Settings, Gift, Plus, Flame } from "lucide-react";

interface Chore {
  id: string;
  name: string;
  base_points: number;
  leverage: number;
  is_urgent: boolean;
}

interface Reward {
  id: string;
  name: string;
  points_required: number;
}

/**
 * Parent Dashboard page responsible for managing chores (leverage, urgency)
 * and rewards.
 */
export default function ParentDashboard() {
  const [chores, setChores] = useState<Chore[]>([]);
  const [rewards, setRewards] = useState<Reward[]>([]);
  const [newRewardName, setNewRewardName] = useState("");
  const [newRewardPoints, setNewRewardPoints] = useState<number>(100);

  const fetchChores = async () => {
    const { data, error } = await supabase.from("chores").select("*").order("created_at", { ascending: true });
    if (!error && data) setChores(data);
  };

  const fetchRewards = async () => {
    const { data, error } = await supabase.from("rewards").select("*").order("points_required", { ascending: true });
    if (!error && data) setRewards(data);
  };

  useEffect(() => {
    const loadData = async () => {
      await fetchChores();
      await fetchRewards();
    };
    loadData();

  }, []);

  /**
   * Updates a specific chore's property (leverage or urgency).
   */
  const updateChore = async (id: string, field: string, value: number | boolean) => {
    // Optimistic UI update
    setChores(prev => prev.map(c => c.id === id ? { ...c, [field]: value } : c));

    const { error } = await supabase.from("chores").update({ [field]: value }).eq("id", id);
    if (error) {
      console.error("Error updating chore:", error);
      fetchChores(); // Revert on failure
    }
  };

  /**
   * Adds a new reward to the database.
   */
  const handleAddReward = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRewardName.trim()) return;

    const { error } = await supabase.from("rewards").insert([
      { name: newRewardName, points_required: newRewardPoints }
    ]);

    if (!error) {
      setNewRewardName("");
      setNewRewardPoints(100);
      fetchRewards();
    }
  };

  return (
    <div className="pb-20">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <Settings className="text-blue-500 w-6 h-6" />
          親ダッシュボード
        </h1>
      </div>

      {/* Chore Management Section */}
      <section className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 mb-6">
        <h2 className="text-lg font-bold text-gray-800 flex items-center gap-2 mb-4">
          <ListTodo className="text-indigo-500 w-5 h-5" />
          家事のポイント設定
        </h2>

        <div className="space-y-4">
          {chores.length === 0 ? (
            <p className="text-gray-500 text-sm">家事が登録されていません。</p>
          ) : (
            chores.map(chore => (
              <div key={chore.id} className="bg-gray-50 rounded-xl p-4 border border-gray-200">
                <div className="flex justify-between items-center mb-3">
                  <span className="font-bold text-gray-800 text-lg">{chore.name}</span>
                  <span className="bg-indigo-100 text-indigo-800 text-xs font-bold px-2 py-1 rounded-full">
                    基本: {chore.base_points} pt
                  </span>
                </div>

                {/* Leverage Slider */}
                <div className="mb-4">
                  <div className="flex justify-between text-sm mb-1 text-gray-600">
                    <span>倍率 (レバレッジ)</span>
                    <span className="font-bold text-blue-600">x{chore.leverage}</span>
                  </div>
                  <input
                    type="range"
                    min="1.0"
                    max="3.0"
                    step="0.1"
                    value={chore.leverage}
                    onChange={(e) => updateChore(chore.id, "leverage", parseFloat(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-500"
                  />
                  <div className="flex justify-between text-xs text-gray-400 mt-1">
                    <span>1.0x</span>
                    <span>3.0x</span>
                  </div>
                </div>

                {/* Urgency Toggle */}
                <label className="flex items-center justify-between bg-white p-3 rounded-lg border border-gray-100 cursor-pointer">
                  <div className="flex items-center gap-2">
                    <Flame className={`w-5 h-5 ${chore.is_urgent ? "text-red-500" : "text-gray-300"}`} />
                    <span className="text-sm font-bold text-gray-700">特急モード (+50pt)</span>
                  </div>
                  <div className="relative">
                    <input
                      type="checkbox"
                      className="sr-only"
                      checked={chore.is_urgent}
                      onChange={(e) => updateChore(chore.id, "is_urgent", e.target.checked)}
                    />
                    <div className={`block w-14 h-8 rounded-full transition-colors ${chore.is_urgent ? 'bg-red-500' : 'bg-gray-300'}`}></div>
                    <div className={`dot absolute left-1 top-1 bg-white w-6 h-6 rounded-full transition-transform ${chore.is_urgent ? 'transform translate-x-6' : ''}`}></div>
                  </div>
                </label>
              </div>
            ))
          )}
        </div>
      </section>

      {/* Reward Management Section */}
      <section className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 mb-6">
        <h2 className="text-lg font-bold text-gray-800 flex items-center gap-2 mb-4">
          <Gift className="text-pink-500 w-5 h-5" />
          ごほうび管理
        </h2>

        {/* Add Reward Form */}
        <form onSubmit={handleAddReward} className="flex flex-col gap-3 mb-6 bg-pink-50 p-4 rounded-xl border border-pink-100">
          <div className="flex flex-col gap-1">
            <label className="text-xs font-bold text-gray-600">ごほうび名</label>
            <input
              type="text"
              value={newRewardName}
              onChange={(e) => setNewRewardName(e.target.value)}
              className="p-2 rounded-lg border border-gray-300 w-full focus:ring-2 focus:ring-pink-500 focus:outline-none"
              placeholder="例: ゲーム1時間"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-bold text-gray-600">必要ポイント</label>
            <input
              type="number"
              value={newRewardPoints}
              onChange={(e) => setNewRewardPoints(parseInt(e.target.value) || 0)}
              className="p-2 rounded-lg border border-gray-300 w-full focus:ring-2 focus:ring-pink-500 focus:outline-none"
            />
          </div>
          <button
            type="submit"
            className="mt-2 bg-pink-500 hover:bg-pink-600 text-white font-bold py-3 rounded-xl flex items-center justify-center gap-2 transition-colors"
          >
            <Plus className="w-5 h-5" />
            追加する
          </button>
        </form>

        {/* Existing Rewards List */}
        <div className="space-y-3">
          {rewards.map(reward => (
            <div key={reward.id} className="flex justify-between items-center bg-white border border-gray-200 p-3 rounded-xl">
              <span className="font-bold text-gray-800">{reward.name}</span>
              <span className="text-pink-600 font-bold bg-pink-100 px-3 py-1 rounded-full text-sm">
                {reward.points_required} pt
              </span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

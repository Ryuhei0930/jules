"use client";

import { useState, useEffect } from "react";
import { supabase } from "@/utils/supabase/client";
import { useAuth } from "@/components/AuthProvider";
import { Coins, CheckCircle, Gift, Flame, ArrowUpCircle } from "lucide-react";

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
 * Calculates the current earning potential of a chore.
 */
const calculatePoints = (chore: Chore) => {
  return Math.floor(chore.base_points * chore.leverage) + (chore.is_urgent ? 50 : 0);
};

/**
 * Child Dashboard page where children can view available chores,
 * complete them for points, and exchange points for rewards.
 */
export default function ChildDashboard() {
  const { role } = useAuth();
  const [totalPoints, setTotalPoints] = useState<number>(0);
  const [chores, setChores] = useState<Chore[]>([]);
  const [rewards, setRewards] = useState<Reward[]>([]);
  const [userId, setUserId] = useState<string | null>(null);

  const fetchUserData = async () => {
    // In a real app, use the actual authenticated user ID
    const { data } = await supabase.from("users").select("*").eq("role", "child").limit(1);
    if (data && data.length > 0) {
      setUserId(data[0].id);
      setTotalPoints(data[0].total_points);
    }
  };

  const fetchChores = async () => {
    const { data } = await supabase.from("chores").select("*");
    if (data) {
      // Sort by highest earning potential
      const sorted = data.sort((a, b) => calculatePoints(b) - calculatePoints(a));
      setChores(sorted);
    }
  };

  const fetchRewards = async () => {
    const { data } = await supabase.from("rewards").select("*").order("points_required", { ascending: true });
    if (data) setRewards(data);
  };

  useEffect(() => {
    const loadData = async () => {
      await fetchUserData();
      await fetchChores();
      await fetchRewards();
    };
    loadData();

  }, [role]); // Refetch if role somehow toggles while on this component

  /**
   * Handles chore completion: logs the event and adds points to the user.
   */
  const handleCompleteChore = async (chore: Chore) => {
    if (!userId) return;

    const earned = calculatePoints(chore);
    const newTotal = totalPoints + earned;

    // Optimistic update
    setTotalPoints(newTotal);

    // 1. Insert into logs
    await supabase.from("logs").insert([
      { user_id: userId, chore_id: chore.id, points_earned: earned }
    ]);

    // 2. Update user total points
    await supabase.from("users").update({ total_points: newTotal }).eq("id", userId);
  };

  /**
   * Handles reward exchange: deducts points if user has enough.
   */
  const handleExchangeReward = async (reward: Reward) => {
    if (!userId || totalPoints < reward.points_required) {
      alert("ポイントが足りません！");
      return;
    }

    const newTotal = totalPoints - reward.points_required;

    // Optimistic update
    setTotalPoints(newTotal);

    // Update user total points (In a real app, also insert a 'reward_logs' record)
    await supabase.from("users").update({ total_points: newTotal }).eq("id", userId);
    alert(`「${reward.name}」をゲットしました！`);
  };

  return (
    <div className="pb-20">
      {/* Top Points Display */}
      <div className="bg-gradient-to-br from-yellow-400 to-orange-500 rounded-2xl shadow-lg p-6 mb-8 text-center text-white">
        <h2 className="text-sm font-bold opacity-90 mb-1">現在のポイント</h2>
        <div className="flex items-center justify-center gap-2">
          <Coins className="w-10 h-10 text-yellow-100" />
          <span className="text-5xl font-black tracking-tight">{totalPoints}</span>
          <span className="text-xl font-bold mt-3">pt</span>
        </div>
      </div>

      {/* Available Chores Section */}
      <section className="mb-8">
        <h3 className="text-xl font-black text-gray-800 mb-4 flex items-center gap-2">
          <ArrowUpCircle className="w-6 h-6 text-green-500" />
          今稼げる家事！
        </h3>
        <div className="space-y-4">
          {chores.length === 0 ? (
            <p className="text-gray-500 text-sm">家事がありません。</p>
          ) : (
            chores.map((chore) => {
              const points = calculatePoints(chore);
              const isBoosted = chore.leverage > 1.0 || chore.is_urgent;

              return (
                <div
                  key={chore.id}
                  className={`bg-white rounded-2xl shadow-sm border-2 p-4 flex flex-col gap-3 transition-transform active:scale-95 ${
                    isBoosted ? "border-orange-400" : "border-gray-100"
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-black text-lg text-gray-800">{chore.name}</h4>
                      <div className="flex gap-2 mt-1">
                        {chore.leverage > 1.0 && (
                          <span className="text-xs font-bold bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                            {chore.leverage}倍ボーナス！
                          </span>
                        )}
                        {chore.is_urgent && (
                          <span className="text-xs font-bold bg-red-100 text-red-700 px-2 py-0.5 rounded flex items-center gap-1">
                            <Flame className="w-3 h-3" /> 特急 (+50pt)
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-black text-orange-500">{points}<span className="text-sm">pt</span></div>
                    </div>
                  </div>

                  <button
                    onClick={() => handleCompleteChore(chore)}
                    className="w-full bg-green-500 hover:bg-green-600 text-white font-black text-lg py-3 rounded-xl flex items-center justify-center gap-2 shadow-sm"
                  >
                    <CheckCircle className="w-6 h-6" />
                    やった！
                  </button>
                </div>
              );
            })
          )}
        </div>
      </section>

      {/* Rewards Section */}
      <section>
        <h3 className="text-xl font-black text-gray-800 mb-4 flex items-center gap-2">
          <Gift className="w-6 h-6 text-pink-500" />
          ごほうび交換
        </h3>
        <div className="grid grid-cols-2 gap-3">
          {rewards.map((reward) => {
            const canAfford = totalPoints >= reward.points_required;
            return (
              <div
                key={reward.id}
                className={`bg-white rounded-2xl border-2 p-4 flex flex-col items-center justify-center text-center gap-2 ${
                  canAfford ? "border-pink-300" : "border-gray-100 opacity-60"
                }`}
              >
                <span className="font-bold text-gray-800 line-clamp-2">{reward.name}</span>
                <span className="text-pink-600 font-black">{reward.points_required} pt</span>
                <button
                  onClick={() => handleExchangeReward(reward)}
                  disabled={!canAfford}
                  className={`mt-2 w-full py-2 rounded-lg font-bold text-sm transition-colors ${
                    canAfford
                      ? "bg-pink-100 text-pink-700 hover:bg-pink-200"
                      : "bg-gray-100 text-gray-400 cursor-not-allowed"
                  }`}
                >
                  交換する
                </button>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}

import { createClient } from "@supabase/supabase-js";

/**
 * Initializes and exports the Supabase client instance.
 * Note: In a real production application, these values should be securely managed
 * in environment variables. For this prototype/PWA, they need to be populated.
 */
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "https://placeholder-project.supabase.co";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "placeholder-anon-key";

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

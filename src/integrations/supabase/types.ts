export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "12.2.3 (519615d)"
  }
  public: {
    Tables: {
      agent_conversations: {
        Row: {
          agent_id: string
          conversation_id: string
          created_at: string
          id: string
          message: string
          response: string
          timestamp: string
          user_id: string
        }
        Insert: {
          agent_id: string
          conversation_id: string
          created_at?: string
          id?: string
          message: string
          response: string
          timestamp?: string
          user_id: string
        }
        Update: {
          agent_id?: string
          conversation_id?: string
          created_at?: string
          id?: string
          message?: string
          response?: string
          timestamp?: string
          user_id?: string
        }
        Relationships: []
      }
      categories: {
        Row: {
          created_at: string
          description: string | null
          icon: string | null
          id: string
          name: string
          parent_id: string | null
          portal_id: string
          updated_at: string
        }
        Insert: {
          created_at?: string
          description?: string | null
          icon?: string | null
          id?: string
          name: string
          parent_id?: string | null
          portal_id?: string
          updated_at?: string
        }
        Update: {
          created_at?: string
          description?: string | null
          icon?: string | null
          id?: string
          name?: string
          parent_id?: string | null
          portal_id?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "categories_parent_id_fkey"
            columns: ["parent_id"]
            isOneToOne: false
            referencedRelation: "categories"
            referencedColumns: ["id"]
          },
        ]
      }
      comments: {
        Row: {
          content: string
          created_at: string
          id: string
          parent_id: string | null
          portal_id: string
          post_id: string
          updated_at: string
          user_id: string
        }
        Insert: {
          content: string
          created_at?: string
          id?: string
          parent_id?: string | null
          portal_id?: string
          post_id: string
          updated_at?: string
          user_id: string
        }
        Update: {
          content?: string
          created_at?: string
          id?: string
          parent_id?: string | null
          portal_id?: string
          post_id?: string
          updated_at?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "comments_parent_id_fkey"
            columns: ["parent_id"]
            isOneToOne: false
            referencedRelation: "comments"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "comments_post_id_fkey"
            columns: ["post_id"]
            isOneToOne: false
            referencedRelation: "posts"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "fk_comments_post"
            columns: ["post_id"]
            isOneToOne: false
            referencedRelation: "posts"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "fk_comments_user_profiles"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "profiles"
            referencedColumns: ["user_id"]
          },
        ]
      }
      jobs: {
        Row: {
          company: string
          created_at: string
          description: string | null
          external_url: string
          id: string
          location: string | null
          posted_date: string | null
          remote: boolean | null
          salary_currency: string | null
          salary_max: number | null
          salary_min: number | null
          scraped_at: string
          source: string
          tech_stack: string[] | null
          title: string
          updated_at: string
        }
        Insert: {
          company: string
          created_at?: string
          description?: string | null
          external_url: string
          id?: string
          location?: string | null
          posted_date?: string | null
          remote?: boolean | null
          salary_currency?: string | null
          salary_max?: number | null
          salary_min?: number | null
          scraped_at?: string
          source?: string
          tech_stack?: string[] | null
          title: string
          updated_at?: string
        }
        Update: {
          company?: string
          created_at?: string
          description?: string | null
          external_url?: string
          id?: string
          location?: string | null
          posted_date?: string | null
          remote?: boolean | null
          salary_currency?: string | null
          salary_max?: number | null
          salary_min?: number | null
          scraped_at?: string
          source?: string
          tech_stack?: string[] | null
          title?: string
          updated_at?: string
        }
        Relationships: []
      }
      newsletter_subscriptions: {
        Row: {
          created_at: string
          email: string
          full_name: string | null
          id: string
          interests: string[] | null
          is_active: boolean
          subscription_type: string
          updated_at: string
        }
        Insert: {
          created_at?: string
          email: string
          full_name?: string | null
          id?: string
          interests?: string[] | null
          is_active?: boolean
          subscription_type?: string
          updated_at?: string
        }
        Update: {
          created_at?: string
          email?: string
          full_name?: string | null
          id?: string
          interests?: string[] | null
          is_active?: boolean
          subscription_type?: string
          updated_at?: string
        }
        Relationships: []
      }
      post_tags: {
        Row: {
          post_id: string
          tag_id: string
        }
        Insert: {
          post_id: string
          tag_id: string
        }
        Update: {
          post_id?: string
          tag_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "post_tags_post_id_fkey"
            columns: ["post_id"]
            isOneToOne: false
            referencedRelation: "posts"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "post_tags_tag_id_fkey"
            columns: ["tag_id"]
            isOneToOne: false
            referencedRelation: "tags"
            referencedColumns: ["id"]
          },
        ]
      }
      posts: {
        Row: {
          category_id: string | null
          content: string
          created_at: string
          external_url: string | null
          id: string
          portal_id: string
          reddit_id: string | null
          source: string | null
          title: string
          type: string
          updated_at: string
          user_id: string
        }
        Insert: {
          category_id?: string | null
          content: string
          created_at?: string
          external_url?: string | null
          id?: string
          portal_id?: string
          reddit_id?: string | null
          source?: string | null
          title: string
          type?: string
          updated_at?: string
          user_id: string
        }
        Update: {
          category_id?: string | null
          content?: string
          created_at?: string
          external_url?: string | null
          id?: string
          portal_id?: string
          reddit_id?: string | null
          source?: string | null
          title?: string
          type?: string
          updated_at?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "fk_posts_category"
            columns: ["category_id"]
            isOneToOne: false
            referencedRelation: "categories"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "fk_posts_user_profiles"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "profiles"
            referencedColumns: ["user_id"]
          },
          {
            foreignKeyName: "posts_category_id_fkey"
            columns: ["category_id"]
            isOneToOne: false
            referencedRelation: "categories"
            referencedColumns: ["id"]
          },
        ]
      }
      profiles: {
        Row: {
          avatar_url: string | null
          bio: string | null
          created_at: string
          display_name: string | null
          email: string | null
          full_name: string | null
          id: string
          updated_at: string
          user_id: string
          username: string | null
          website: string | null
        }
        Insert: {
          avatar_url?: string | null
          bio?: string | null
          created_at?: string
          display_name?: string | null
          email?: string | null
          full_name?: string | null
          id?: string
          updated_at?: string
          user_id: string
          username?: string | null
          website?: string | null
        }
        Update: {
          avatar_url?: string | null
          bio?: string | null
          created_at?: string
          display_name?: string | null
          email?: string | null
          full_name?: string | null
          id?: string
          updated_at?: string
          user_id?: string
          username?: string | null
          website?: string | null
        }
        Relationships: []
      }
      tags: {
        Row: {
          color: string | null
          created_at: string
          id: string
          name: string
        }
        Insert: {
          color?: string | null
          created_at?: string
          id?: string
          name: string
        }
        Update: {
          color?: string | null
          created_at?: string
          id?: string
          name?: string
        }
        Relationships: []
      }
      user_roles: {
        Row: {
          created_at: string | null
          id: string
          role: Database["public"]["Enums"]["user_role"]
          user_id: string
        }
        Insert: {
          created_at?: string | null
          id?: string
          role?: Database["public"]["Enums"]["user_role"]
          user_id: string
        }
        Update: {
          created_at?: string | null
          id?: string
          role?: Database["public"]["Enums"]["user_role"]
          user_id?: string
        }
        Relationships: []
      }
      votes: {
        Row: {
          created_at: string
          id: string
          tool_id: string
          user_id: string
        }
        Insert: {
          created_at?: string
          id?: string
          tool_id: string
          user_id: string
        }
        Update: {
          created_at?: string
          id?: string
          tool_id?: string
          user_id?: string
        }
        Relationships: []
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      is_admin: {
        Args: { user_uuid: string }
        Returns: boolean
      }
    }
    Enums: {
      user_role: "admin" | "moderator" | "user"
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {
      user_role: ["admin", "moderator", "user"],
    },
  },
} as const

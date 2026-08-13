import { apiClient } from "./client";
import type { MciScore } from "@/types/mci";

// نقاط نهاية MCI الحقيقية على الـbackend الفعلي (/api/v1/mci/trainees/{uuid}/*)،
// بمعرّف trainee حقيقي (uuid). الدوال القديمة (listFactors/computeMci برقم
// مستخدم عددي) استدعت نقاط نهاية وهمية غير موجودة أصلًا على الـbackend
// الحقيقي (/api/factors, /api/users/{id}/mci) وكانت مستخدَمة فقط من لوحات
// mci-score اليتيمة التي أُزيلت لأنها كانت تكسر البناء بالفعل قبل هذا
// الإصلاح — لذا حُذفت هذه الدوال معها بدل إبقاء كود ميت غير قابل للتصريف.
export const mciApi = {
  calculate: async (traineeId: string): Promise<MciScore> => {
    const { data } = await apiClient.post<MciScore>(`/api/v1/mci/trainees/${traineeId}/calculate`);
    return data;
  },
  getLatest: async (traineeId: string): Promise<MciScore | null> => {
    try {
      const { data } = await apiClient.get<MciScore>(`/api/v1/mci/trainees/${traineeId}/latest`);
      return data;
    } catch {
      return null;
    }
  },
  getHistory: async (traineeId: string): Promise<MciScore[]> => {
    const { data } = await apiClient.get<MciScore[]>(`/api/v1/mci/trainees/${traineeId}/history`);
    return data;
  },
};

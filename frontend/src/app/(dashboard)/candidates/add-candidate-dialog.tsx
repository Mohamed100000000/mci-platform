"use client";
import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Plus } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger,
} from "@/components/ui/dialog";
import { useCreateCandidate } from "@/hooks/use-candidates";

const schema = z.object({
  trainee_code: z.string().min(1, "Trainee code is required"),
  full_name: z.string().min(2, "Full name is required"),
  nationality: z.string().optional(),
  rank: z.string().optional(),
  email: z.string().email("Enter a valid email").optional().or(z.literal("")),
});
type FormValues = z.infer<typeof schema>;

export function AddCandidateDialog() {
  const [open, setOpen] = React.useState(false);
  const createCandidate = useCreateCandidate();

  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema),
  });

  const onSubmit = (values: FormValues) => {
    createCandidate.mutate(
      { ...values, email: values.email || undefined },
      {
        onSuccess: () => {
          toast.success(`${values.full_name} added successfully.`);
          reset();
          setOpen(false);
        },
        onError: () => toast.error("Could not reach the API. Is the backend running?"),
      }
    );
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4" /> New candidate
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add candidate</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="trainee_code">Trainee code</Label>
            <Input id="trainee_code" placeholder="TR-2026-0142" {...register("trainee_code")} />
            {errors.trainee_code && <p className="text-xs text-danger">{errors.trainee_code.message}</p>}
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="full_name">Full name</Label>
            <Input id="full_name" placeholder="Ahmed Al-Fahad" {...register("full_name")} />
            {errors.full_name && <p className="text-xs text-danger">{errors.full_name.message}</p>}
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label htmlFor="nationality">Nationality</Label>
              <Input id="nationality" placeholder="Saudi Arabia" {...register("nationality")} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="rank">Rank</Label>
              <Input id="rank" placeholder="Able Seafarer Deck" {...register("rank")} />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" placeholder="trainee@example.com" {...register("email")} />
            {errors.email && <p className="text-xs text-danger">{errors.email.message}</p>}
          </div>
          <DialogFooter>
            <Button type="submit" disabled={createCandidate.isPending}>
              {createCandidate.isPending ? "Adding..." : "Add candidate"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

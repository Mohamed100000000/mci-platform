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
  full_name: z.string().min(2, "Full name is required"),
  nationality: z.string().optional(),
  current_position: z.string().optional(),
  years_of_experience: z.number().min(0).max(60).optional(),
});
type FormValues = z.infer<typeof schema>;

export function AddCandidateDialog() {
  const [open, setOpen] = React.useState(false);
  const createCandidate = useCreateCandidate();

  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { years_of_experience: 0 },
  });

  const onSubmit = (values: FormValues) => {
    createCandidate.mutate(values, {
      onSuccess: () => {
        toast.success(`${values.full_name} added successfully.`);
        reset();
        setOpen(false);
      },
      onError: () => toast.error("Could not reach the API. Is the backend running?"),
    });
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
              <Label htmlFor="years_of_experience">Years of experience</Label>
              <Input id="years_of_experience" type="number" step="0.5" {...register("years_of_experience", { valueAsNumber: true })} />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="current_position">Current position</Label>
            <Input id="current_position" placeholder="Able Seafarer Deck" {...register("current_position")} />
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

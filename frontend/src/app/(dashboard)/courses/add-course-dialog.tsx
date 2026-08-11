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
import { useCreateCourse } from "@/hooks/use-courses";

const schema = z.object({
  code: z.string().min(1, "Course code is required"),
  title: z.string().min(2, "Title is required"),
  stcw_reference: z.string().optional(),
  duration_hours: z.string().optional(),
  max_capacity: z.string().optional(),
});
type FormValues = z.infer<typeof schema>;

export function AddCourseDialog() {
  const [open, setOpen] = React.useState(false);
  const createCourse = useCreateCourse();

  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema),
  });

  const onSubmit = (values: FormValues) => {
    createCourse.mutate(
      {
        ...values,
        duration_hours: values.duration_hours ? Number(values.duration_hours) : undefined,
        max_capacity: values.max_capacity ? Number(values.max_capacity) : undefined,
      },
      {
      onSuccess: () => {
        toast.success(`${values.title} added successfully.`);
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
          <Plus className="h-4 w-4" /> New course
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add course</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="code">Course code</Label>
            <Input id="code" placeholder="STCW-PST" {...register("code")} />
            {errors.code && <p className="text-xs text-danger">{errors.code.message}</p>}
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="title">Title</Label>
            <Input id="title" placeholder="Personal Survival Techniques" {...register("title")} />
            {errors.title && <p className="text-xs text-danger">{errors.title.message}</p>}
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="stcw_reference">STCW reference</Label>
            <Input id="stcw_reference" placeholder="A-VI/1-1" {...register("stcw_reference")} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label htmlFor="duration_hours">Duration (hrs)</Label>
              <Input id="duration_hours" type="number" placeholder="16" {...register("duration_hours")} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="max_capacity">Max capacity</Label>
              <Input id="max_capacity" type="number" placeholder="20" {...register("max_capacity")} />
            </div>
          </div>
          <DialogFooter>
            <Button type="submit" disabled={createCourse.isPending}>
              {createCourse.isPending ? "Adding..." : "Add course"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

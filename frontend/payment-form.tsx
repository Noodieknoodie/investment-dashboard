"use client"

import type React from "react"

import { useState } from "react"
import { CalendarIcon, Paperclip } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Calendar } from "@/components/ui/calendar"
import { Switch } from "@/components/ui/switch"
import { cn } from "@/lib/utils"
import { format } from "date-fns"
import type { PaymentFormData } from "./types"

interface PaymentFormProps {
  clientId: string
  initialData?: PaymentFormData
  onCancel: () => void
  isEditing: boolean
}

export function PaymentForm({ clientId, initialData, onCancel, isEditing }: PaymentFormProps) {
  const [formData, setFormData] = useState<PaymentFormData>(
    initialData || {
      receivedDate: format(new Date(), "yyyy-MM-dd"),
      appliedPeriod: "single",
      periodValue: "",
      startPeriod: "",
      endPeriod: "",
      aum: "",
      amount: "",
      method: "",
      notes: "",
      attachmentUrl: "",
    },
  )
  const [date, setDate] = useState<Date | undefined>(
    initialData?.receivedDate ? new Date(initialData.receivedDate) : new Date(),
  )
  const [isSplitPayment, setIsSplitPayment] = useState(formData.appliedPeriod === "multiple")
  const [hasChanges, setHasChanges] = useState(false)
  const [customMethod, setCustomMethod] = useState("")
  const [isNotesOpen, setIsNotesOpen] = useState(!!formData.notes || !!formData.attachmentUrl)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    setHasChanges(true)
  }

  const handleSelectChange = (name: string, value: string) => {
    setFormData((prev) => ({ ...prev, [name]: value }))
    setHasChanges(true)
  }

  const handleDateChange = (newDate: Date | undefined) => {
    setDate(newDate)
    if (newDate) {
      setFormData((prev) => ({ ...prev, receivedDate: format(newDate, "yyyy-MM-dd") }))
      setHasChanges(true)
    }
  }

  const handleSplitPaymentToggle = (checked: boolean) => {
    setIsSplitPayment(checked)
    setFormData((prev) => ({
      ...prev,
      appliedPeriod: checked ? "multiple" : "single",
      periodValue: "",
      startPeriod: "",
      endPeriod: "",
    }))
    setHasChanges(true)
  }

  const handleAttachFile = () => {
    // Implement file attachment logic here
    console.log("File attachment triggered")
    setHasChanges(true)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Implement form submission logic here
    console.log("Submitting payment:", formData)
    setHasChanges(false)
  }

  const handleCancel = () => {
    onCancel()
  }

  const handleClear = () => {
    if (hasChanges) {
      // Implement confirmation dialog logic here
      console.log("Clearing form with changes")
    }
    setFormData({
      receivedDate: format(new Date(), "yyyy-MM-dd"),
      appliedPeriod: "single",
      periodValue: "",
      startPeriod: "",
      endPeriod: "",
      aum: "",
      amount: "",
      method: "",
      notes: "",
      attachmentUrl: "",
    })
    setDate(new Date())
    setIsSplitPayment(false)
    setCustomMethod("")
    setHasChanges(false)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div className="space-y-1.5">
          <Label htmlFor="receivedDate" className="text-sm font-medium">
            Received Date
          </Label>
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                className={cn("w-full h-10 justify-start text-left font-normal", !date && "text-muted-foreground")}
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {date ? format(date, "PPP") : <span>Pick a date</span>}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar mode="single" selected={date} onSelect={handleDateChange} initialFocus />
            </PopoverContent>
          </Popover>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="appliedPeriod" className="text-sm font-medium">
              Applied Period
            </Label>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-muted-foreground">Single</span>
              <Switch checked={isSplitPayment} onCheckedChange={handleSplitPaymentToggle} />
              <span className="text-sm text-muted-foreground">Split</span>
            </div>
          </div>
          <div className="flex space-x-2">
            {isSplitPayment ? (
              <>
                <Select
                  value={formData.startPeriod}
                  onValueChange={(value) => handleSelectChange("startPeriod", value)}
                >
                  <SelectTrigger className="h-10 flex-1">
                    <SelectValue placeholder="Start period" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="q1-2023">Q1 2023</SelectItem>
                    <SelectItem value="q2-2023">Q2 2023</SelectItem>
                    <SelectItem value="q3-2023">Q3 2023</SelectItem>
                    <SelectItem value="q4-2023">Q4 2023</SelectItem>
                    <SelectItem value="q1-2024">Q1 2024</SelectItem>
                    <SelectItem value="q2-2024">Q2 2024</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={formData.endPeriod} onValueChange={(value) => handleSelectChange("endPeriod", value)}>
                  <SelectTrigger className="h-10 flex-1">
                    <SelectValue placeholder="End period" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="q1-2023">Q1 2023</SelectItem>
                    <SelectItem value="q2-2023">Q2 2023</SelectItem>
                    <SelectItem value="q3-2023">Q3 2023</SelectItem>
                    <SelectItem value="q4-2023">Q4 2023</SelectItem>
                    <SelectItem value="q1-2024">Q1 2024</SelectItem>
                    <SelectItem value="q2-2024">Q2 2024</SelectItem>
                  </SelectContent>
                </Select>
              </>
            ) : (
              <Select value={formData.periodValue} onValueChange={(value) => handleSelectChange("periodValue", value)}>
                <SelectTrigger className="w-full h-10">
                  <SelectValue placeholder="Select period" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="q1-2023">Q1 2023</SelectItem>
                  <SelectItem value="q2-2023">Q2 2023</SelectItem>
                  <SelectItem value="q3-2023">Q3 2023</SelectItem>
                  <SelectItem value="q4-2023">Q4 2023</SelectItem>
                  <SelectItem value="q1-2024">Q1 2024</SelectItem>
                  <SelectItem value="q2-2024">Q2 2024</SelectItem>
                </SelectContent>
              </Select>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="space-y-2">
          <Label htmlFor="aum" className="text-sm font-medium">
            Assets Under Management <span className="text-xs text-muted-foreground">(optional)</span>
          </Label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground">$</span>
            <Input
              id="aum"
              name="aum"
              type="number"
              value={formData.aum}
              onChange={handleInputChange}
              placeholder="0.00"
              className="pl-8 h-10"
            />
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="amount" className="text-sm font-medium">
            Payment Amount
          </Label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground">$</span>
            <Input
              id="amount"
              name="amount"
              type="number"
              value={formData.amount}
              onChange={handleInputChange}
              placeholder="0.00"
              required
              className="pl-8 h-10"
            />
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="method" className="text-sm font-medium">
            Payment Method <span className="text-xs text-muted-foreground">(optional)</span>
          </Label>
          <Select value={formData.method} onValueChange={(value) => handleSelectChange("method", value)}>
            <SelectTrigger className="h-10">
              <SelectValue placeholder="Select method" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="check">Check</SelectItem>
              <SelectItem value="wire">Wire Transfer</SelectItem>
              <SelectItem value="ach">ACH</SelectItem>
              <SelectItem value="other">Other</SelectItem>
            </SelectContent>
          </Select>
          {formData.method === "other" && (
            <Input
              name="customMethod"
              value={customMethod}
              onChange={(e) => setCustomMethod(e.target.value)}
              placeholder="Specify method"
              className="mt-2 h-10"
            />
          )}
        </div>
      </div>

      {/* Modified layout to position buttons next to the notes section in a horizontal arrangement */}
      <div className="flex flex-col md:flex-row gap-5">
        {/* Notes & Attachments section - takes up more space */}
        <div className="flex-1">
          <details className="group">
            <summary className="flex items-center cursor-pointer list-none">
              <Label htmlFor="notes" className="text-sm font-medium">
                Notes & Attachments <span className="text-xs text-muted-foreground">(optional)</span>
              </Label>
              <svg
                className="ml-2 h-4 w-4 group-open:rotate-180 transition-transform"
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <polyline points="6 9 12 15 18 9" />
              </svg>
            </summary>
            <div className="pt-2 pb-1">
              <div className="relative">
                <Textarea
                  id="notes"
                  name="notes"
                  value={formData.notes}
                  onChange={handleInputChange}
                  placeholder="Add any additional notes here"
                  rows={3}
                  className="resize-none min-h-[80px]"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="absolute right-2 bottom-2 opacity-80 hover:opacity-100"
                  onClick={handleAttachFile}
                  title="Attach a file"
                >
                  <Paperclip className="h-4 w-4" />
                  <span className="sr-only">Attach file</span>
                </Button>
              </div>
              {formData.attachmentUrl && <div className="text-sm text-blue-600 mt-1">1 attachment</div>}
            </div>
          </details>
        </div>

        {/* Buttons section - horizontal layout */}
        <div className="md:flex md:items-end md:space-x-3 space-y-3 md:space-y-0">
          {isEditing && (
            <Button type="button" variant="outline" onClick={handleCancel}>
              Cancel
            </Button>
          )}
          <Button type="button" variant="outline" onClick={handleClear}>
            Clear
          </Button>
          <Button type="submit">{isEditing ? "Update" : "Submit"}</Button>
        </div>
      </div>
    </form>
  )
}


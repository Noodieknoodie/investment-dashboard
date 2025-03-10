"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { CalendarIcon, Paperclip, Loader2, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Calendar } from "@/components/ui/calendar"
import { Switch } from "@/components/ui/switch"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { cn } from "@/lib/utils"
import { format } from "date-fns"
import { paymentApi, apiRequest } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"
import { formatPeriod } from "@/lib/mappers"
import type { PaymentFormData } from "../../types"

interface PaymentFormProps {
  clientId: string
  contractId: string
  initialData?: PaymentFormData
  onCancel: () => void
  onSubmit: (data: PaymentFormData) => Promise<boolean>
  isEditing: boolean
  isLoading?: boolean
  previousPayments?: Array<{ amount: number, date: string }>
}

// Add this helper to validate client/contract relationship
// We can't trust that the parent component has done this validation correctly
function useClientContractValidation(clientId: string, contractId: string) {
  const [isValid, setIsValid] = useState<boolean | null>(null);
  const [isChecking, setIsChecking] = useState<boolean>(false);
  const [retries, setRetries] = useState<number>(0);
  
  useEffect(() => {
    // Reset validation state when either ID changes
    setIsValid(null);
    setIsChecking(true); // Start checking immediately
    setRetries(0); // Reset retries
    
    // Skip validation if we don't have both IDs
    if (!clientId || !contractId) {
      setIsChecking(false);
      return;
    }
    
    console.log(`🔎 [VALIDATION] Checking if contract ${contractId} belongs to client ${clientId}...`);
    
    let isMounted = true;
    let validationTimeout: NodeJS.Timeout;
    
    const validateRelationship = async () => {
      try {
        // Add a deliberate delay to avoid race conditions
        // This ensures we don't fetch data before client/contract relationship is confirmed
        await new Promise(resolve => setTimeout(resolve, 200));
        
        if (!isMounted) return;
        
        // Get client data to check contracts
        const response = await fetch(`http://localhost:8000/clients/${clientId}`);
        if (!response.ok) {
          throw new Error(`Failed to fetch client data: ${response.statusText}`);
        }
        
        if (!isMounted) return;
        
        const data = await response.json();
        
        if (!isMounted) return;
        
        // Check if this contract belongs to this client
        const isValidContract = data.contracts && 
          Array.isArray(data.contracts) && 
          data.contracts.some((c: { contract_id: number }) => c.contract_id === parseInt(contractId, 10));
        
        // Log the validation result more prominently
        if (isValidContract) {
          console.log(`✅ [VALIDATION SUCCESS] Contract ${contractId} belongs to client ${clientId}`);
          setIsValid(true);
          setIsChecking(false);
        } else {
          console.error(`❌ [VALIDATION FAILED] Contract ${contractId} does NOT belong to client ${clientId}`);
          console.error(`Valid contracts for client ${clientId}: `, 
            data.contracts?.map((c: { contract_id: number }) => c.contract_id).join(', ') || 'None');
            
          // If validation fails and we have few retries, try again after a delay
          // This helps in race conditions when client data is still loading
          if (retries < 3) {
            console.log(`⏳ [VALIDATION] Retry ${retries + 1}/3 in 500ms...`);
            
            // Increment retries
            setRetries(prev => prev + 1);
            
            // Schedule the next retry
            validationTimeout = setTimeout(() => {
              if (isMounted) validateRelationship();
            }, 500);
          } else {
            console.error(`❌ [VALIDATION] All retries failed for client ${clientId}, contract ${contractId}`);
            setIsValid(false);
            setIsChecking(false);
          }
        }
      } catch (error) {
        console.error('[VALIDATION ERROR]', error);
        
        // Retry on error too
        if (retries < 3) {
          console.log(`⏳ [VALIDATION] Retry ${retries + 1}/3 after error...`);
          setRetries(prev => prev + 1);
          validationTimeout = setTimeout(() => {
            if (isMounted) validateRelationship();
          }, 500);
        } else {
          setIsValid(false);
          setIsChecking(false);
        }
      }
    };
    
    validateRelationship();
    
    // Cleanup function
    return () => {
      isMounted = false;
      clearTimeout(validationTimeout);
    };
  }, [clientId, contractId, retries]);
  
  return { isValid, isChecking };
}

export function PaymentForm({
  clientId,
  contractId,
  initialData,
  onCancel,
  onSubmit,
  isEditing,
  isLoading = false,
  previousPayments = []
}: PaymentFormProps) {
  const { toast } = useToast();
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
  const [isSplitPayment, setIsSplitPayment] = useState(initialData?.appliedPeriod === "multiple")
  const [hasChanges, setHasChanges] = useState(false)
  const [customMethod, setCustomMethod] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [availablePeriods, setAvailablePeriods] = useState<{ label: string, value: { quarter?: number, month?: number, year: number } }[]>([])
  const [isMonthly, setIsMonthly] = useState(false)
  const [isNotesOpen, setIsNotesOpen] = useState(!!initialData?.notes || !!initialData?.attachmentUrl)
  const [validationError, setValidationError] = useState<string | null>(null)
  const [expectedFee, setExpectedFee] = useState<number | null>(null)
  const [periodsLoading, setPeriodsLoading] = useState(false)

  // Add validation
  const { isValid: isValidRelationship, isChecking: isValidating } = useClientContractValidation(clientId, contractId);

  // Fetch available periods when contractId changes - BUT ONLY IF VALIDATED
  useEffect(() => {
    // Don't fetch if we don't have valid IDs or if the relationship is invalid
    if (!contractId || !clientId || isValidRelationship === false) {
      return;
    }
    
    // Wait for validation to complete
    if (isValidating || isValidRelationship === null) {
      console.log('Waiting for client/contract validation...');
      return;
    }
    
    // Reset form data when client/contract changes to prevent using invalid data
    if (!isEditing) {
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
      });
      setExpectedFee(null);
    }
    
    console.log(`✅ VALIDATED: Client ${clientId} owns Contract ${contractId} - Fetching periods...`);
    setPeriodsLoading(true);
    
    const fetchPeriods = async () => {
      try {
        const periodsData = await paymentApi.getAvailablePeriods(parseInt(clientId, 10), parseInt(contractId, 10));
        console.log(`Successfully fetched periods for client=${clientId} contract=${contractId}`);
        setAvailablePeriods(periodsData.periods);
        setIsMonthly(periodsData.is_monthly);
      } catch (error) {
        console.error(`Error fetching periods:`, error);
        toast({
          title: "Error loading periods",
          description: "Could not load available payment periods",
          variant: "destructive",
        });
      } finally {
        setPeriodsLoading(false);
      }
    };

    fetchPeriods();
  }, [clientId, contractId, isEditing, toast, isValidRelationship, isValidating]);

  // Calculate expected fee when AUM or period changes
  useEffect(() => {
    const calculateExpectedFee = async () => {
      if (!contractId || (!formData.aum && !formData.periodValue)) return;

      try {
        // Only calculate if we have a period and/or AUM
        if (formData.periodValue) {
          const [periodValue, periodYear] = formData.periodValue.split('-');

          // Log the request data for debugging
          console.log("💰 FEE CALCULATION REQUEST:", {
            client_id: parseInt(clientId, 10),
            contract_id: parseInt(contractId, 10),
            total_assets: formData.aum ? parseInt(formData.aum, 10) : undefined,
            period_type: isMonthly ? 'month' : 'quarter',
            period: parseInt(periodValue, 10),
            year: parseInt(periodYear, 10)
          });

          const feeData = await paymentApi.calculateExpectedFee({
            client_id: parseInt(clientId, 10),
            contract_id: parseInt(contractId, 10),
            total_assets: formData.aum ? parseInt(formData.aum, 10) : undefined,
            period_type: isMonthly ? 'month' : 'quarter',
            period: parseInt(periodValue, 10),
            year: parseInt(periodYear, 10)
          });

          // Log the response for debugging
          console.log("💰 FEE CALCULATION RESPONSE:", feeData);

          // Fix: Check for undefined and provide null as fallback
          setExpectedFee(feeData.expected_fee !== undefined && feeData.expected_fee !== null ?
            Number(feeData.expected_fee) : null);
          
          // Log the final expected fee value
          console.log("💰 EXPECTED FEE SET TO:", feeData.expected_fee);
        }
      } catch (error) {
        console.error("❌ Error calculating expected fee:", error);
        setExpectedFee(null);
      }
    };

    // Call calculate fee when initialized with data or when values change
    calculateExpectedFee();
  }, [clientId, contractId, formData.aum, formData.periodValue, isMonthly]);

  // Validate that endPeriod is after startPeriod if split payment
  useEffect(() => {
    if (isSplitPayment && formData.startPeriod && formData.endPeriod) {
      const [startPeriod, startYear] = formData.startPeriod.split('-').map(val => parseInt(val, 10));
      const [endPeriod, endYear] = formData.endPeriod.split('-').map(val => parseInt(val, 10));

      const startTotal = startYear * (isMonthly ? 12 : 4) + startPeriod;
      const endTotal = endYear * (isMonthly ? 12 : 4) + endPeriod;

      if (endTotal < startTotal) {
        setValidationError("End period cannot be before start period");
      } else {
        setValidationError(null);
      }
    } else {
      setValidationError(null);
    }
  }, [formData.startPeriod, formData.endPeriod, isSplitPayment, isMonthly]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    setHasChanges(true)
  }

  const handleSelectChange = (name: string, value: string) => {
    setFormData((prev) => ({ ...prev, [name]: value }))
    setHasChanges(true)

    // If changing periodValue, also update start/end periods for split payments
    if (name === "periodValue") {
      setFormData((prev) => ({
        ...prev,
        startPeriod: value,
        endPeriod: value
      }));
    }
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
      // When toggling to single, set both start and end to the current periodValue
      ...(checked ? {} : { 
        startPeriod: prev.periodValue || prev.startPeriod, 
        endPeriod: prev.periodValue || prev.startPeriod 
      })
    }))
    
    // Update periodValue when toggling from split to single
    if (!checked && formData.startPeriod) {
      setFormData((prev) => ({
        ...prev,
        periodValue: prev.startPeriod
      }));
    }
    
    setHasChanges(true)
  }

  const handleAttachFile = () => {
    // IMPROVED: Document Feature Messaging
    toast({
      title: "Document Upload Coming Soon",
      description: "Document management will be available in a future update.",
    });
    setHasChanges(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (isSubmitting) return;

    // First check for validation errors
    if (validationError) {
      toast({
        title: "Validation Error",
        description: validationError,
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);

    try {
      // Validate form
      if (!formData.amount) {
        toast({
          title: "Validation Error",
          description: "Payment amount is required.",
          variant: "destructive",
        });
        setIsSubmitting(false);
        return;
      }

      if (isSplitPayment && (!formData.startPeriod || !formData.endPeriod)) {
        toast({
          title: "Validation Error",
          description: "Start and end periods are required for split payments.",
          variant: "destructive",
        });
        setIsSubmitting(false);
        return;
      }

      if (!isSplitPayment && !formData.periodValue) {
        toast({
          title: "Validation Error",
          description: "Applied period is required.",
          variant: "destructive",
        });
        setIsSubmitting(false);
        return;
      }
      
      // IMPROVED: Check for huge payment variance
      const newAmount = parseFloat(formData.amount as string);
      const previousPayment = previousPayments.length > 0 ? previousPayments[0].amount : null;

      if (previousPayment && !isEditing) {
        const percentChange = Math.abs((newAmount - previousPayment) / previousPayment);

        if (percentChange > 0.5) { // 50% change in either direction
          const confirmProceed = window.confirm(
            `This payment amount ($${newAmount.toFixed(2)}) is significantly different (${(percentChange * 100).toFixed(0)}% change) from the previous payment ($${previousPayment.toFixed(2)}). Are you sure this is correct?`
          );
          if (!confirmProceed) {
            setIsSubmitting(false);
            return;
          }
        }
      }

      // Submit form with the contract ID
      const submissionData = {
        ...formData,
        contractId: contractId
      };
      
      const success = await onSubmit(submissionData);

      if (success) {
        toast({
          title: isEditing ? "Payment Updated" : "Payment Created",
          description: isEditing
            ? "The payment has been successfully updated."
            : "A new payment has been successfully created.",
        });

        // Reset form if not editing
        if (!isEditing) {
          handleClear(true);
        }
      } else {
        toast({
          title: "Error",
          description: isEditing
            ? "Failed to update payment. Please try again."
            : "Failed to create payment. Please try again.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error("Form submission error:", error);
      toast({
        title: "Error",
        description: "An unexpected error occurred. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  }

  const handleCancel = () => {
    if (hasChanges) {
      const confirmCancel = window.confirm("You have unsaved changes. Are you sure you want to cancel?");
      if (!confirmCancel) return;
    }
    onCancel();
  }

  const handleClear = (skipConfirmationOrEvent: boolean | React.MouseEvent = false) => {
    // If it's an event, it's from the button click, so don't skip confirmation
    const skipConfirmation = typeof skipConfirmationOrEvent === 'boolean' ? skipConfirmationOrEvent : false;
    
    if (hasChanges && !skipConfirmation) {
      const confirmClear = window.confirm("This will clear all entered data. Continue?");
      if (!confirmClear) return;
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
    });
    setHasChanges(false);
    setDate(new Date());
    setIsSplitPayment(false);
    setExpectedFee(null);
    // Add back any other state resets that were removed
    setCustomMethod("");
    setValidationError(null);
  }

  if (isLoading || periodsLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  // Format the available periods for display
  const formattedPeriods = availablePeriods.map(period => ({
    ...period,
    formattedLabel: period.label
  }));

  // Check if we have a valid contract before rendering the form
  if (!contractId) {
    return (
      <Alert variant="destructive" className="mb-4">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          No valid contract found for this client. Please make sure the client has an active contract.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {validationError && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{validationError}</AlertDescription>
        </Alert>
      )}

      {isEditing && (
        <Alert className="bg-amber-50 border-amber-200">
          <AlertCircle className="h-4 w-4 text-amber-600" />
          <AlertDescription className="text-amber-800">
            Note: To change payment periods, you'll need to delete this payment and create a new one.
          </AlertDescription>
        </Alert>
      )}

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
              <Switch checked={isSplitPayment} onCheckedChange={handleSplitPaymentToggle} disabled={isEditing} />
              <span className="text-sm text-muted-foreground">Split</span>
            </div>
          </div>
          <div className="flex space-x-2">
            {isSplitPayment ? (
              <>
                <Select
                  value={formData.startPeriod}
                  onValueChange={(value) => handleSelectChange("startPeriod", value)}
                  disabled={isEditing}
                >
                  <SelectTrigger className={`h-10 flex-1 ${isEditing ? "opacity-60" : ""}`}>
                    <SelectValue placeholder="Start period (required)" />
                  </SelectTrigger>
                  <SelectContent>
                    {formattedPeriods.map((period) => (
                      <SelectItem key={`start-${period.label}`} value={period.value.quarter
                        ? `${period.value.quarter}-${period.value.year}`
                        : `${period.value.month}-${period.value.year}`}
                      >
                        {period.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Select value={formData.endPeriod} onValueChange={(value) => handleSelectChange("endPeriod", value)} disabled={isEditing}>
                  <SelectTrigger className={`h-10 flex-1 ${isEditing ? "opacity-60" : ""}`}>
                    <SelectValue placeholder="End period (required)" />
                  </SelectTrigger>
                  <SelectContent>
                    {formattedPeriods.map((period) => (
                      <SelectItem key={`end-${period.label}`} value={period.value.quarter
                        ? `${period.value.quarter}-${period.value.year}`
                        : `${period.value.month}-${period.value.year}`}
                      >
                        {period.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </>
            ) : (
              <Select value={formData.periodValue} onValueChange={(value) => handleSelectChange("periodValue", value)} disabled={isEditing}>
                <SelectTrigger className={`w-full h-10 ${isEditing ? "opacity-60" : ""}`}>
                  <SelectValue placeholder="Select period (required)" />
                </SelectTrigger>
                <SelectContent>
                  {formattedPeriods.map((period) => (
                    <SelectItem key={`period-${period.label}`} value={period.value.quarter
                      ? `${period.value.quarter}-${period.value.year}`
                      : `${period.value.month}-${period.value.year}`}
                    >
                      {period.label}
                    </SelectItem>
                  ))}
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
              placeholder="Optional - improves fee calculations"
              className="pl-8 h-10"
            />
          </div>
          {expectedFee !== null && (
            <div className="text-xs text-muted-foreground mt-1">
              Expected Fee: ${expectedFee.toFixed(2)}
            </div>
          )}
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
              placeholder="Enter payment amount (required)"
              required
              className="pl-8 h-10"
            />
          </div>
          {expectedFee !== null && formData.amount && (
            <div className={`text-xs ${Math.abs(parseFloat(formData.amount as string) - expectedFee) <= expectedFee * 0.05
              ? 'text-green-600'
              : Math.abs(parseFloat(formData.amount as string) - expectedFee) <= expectedFee * 0.15
                ? 'text-yellow-600'
                : 'text-red-600'
              }`}>
              {parseFloat(formData.amount as string) > expectedFee
                ? `+${(parseFloat(formData.amount as string) - expectedFee).toFixed(2)} (${((parseFloat(formData.amount as string) - expectedFee) / expectedFee * 100).toFixed(1)}%)`
                : parseFloat(formData.amount as string) < expectedFee
                  ? `-${(expectedFee - parseFloat(formData.amount as string)).toFixed(2)} (${((expectedFee - parseFloat(formData.amount as string)) / expectedFee * 100).toFixed(1)}%)`
                  : 'Matches expected fee'
              }
            </div>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="method" className="text-sm font-medium">
            Payment Method <span className="text-xs text-muted-foreground">(optional)</span>
          </Label>
          <Select
            name="method"
            value={formData.method}
            onValueChange={(value) => handleSelectChange("method", value)}
          >
            <SelectTrigger className="w-full h-10">
              <SelectValue placeholder="Select method (optional)" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Check">Check</SelectItem>
              <SelectItem value="Wire Transfer">Wire Transfer</SelectItem>
              <SelectItem value="ACH">ACH</SelectItem>
              <SelectItem value="Auto - Check">Auto - Check</SelectItem>
              <SelectItem value="Auto - ACH">Auto - ACH</SelectItem>
              <SelectItem value="Invoice - Check">Invoice - Check</SelectItem>
              <SelectItem value="None Specified">None Specified</SelectItem>
              <SelectItem value="Other">Other</SelectItem>
            </SelectContent>
          </Select>
          {formData.method === "Other" && (
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

      {/* Period summary */}
      {(isSplitPayment && formData.startPeriod && formData.endPeriod) && (
        <div className="bg-gray-50 p-3 rounded-md text-sm">
          <h4 className="font-medium mb-1">Payment Summary</h4>
          <div className="text-gray-600">
            {formData.amount && (
              <div>
                {(() => {
                  // Calculate number of periods
                  const [startPeriod, startYear] = formData.startPeriod.split('-').map(val => parseInt(val, 10));
                  const [endPeriod, endYear] = formData.endPeriod.split('-').map(val => parseInt(val, 10));

                  const startTotal = startYear * (isMonthly ? 12 : 4) + startPeriod;
                  const endTotal = endYear * (isMonthly ? 12 : 4) + endPeriod;

                  if (endTotal < startTotal) return "Invalid period range";

                  const periodCount = endTotal - startTotal + 1;
                  const amountPerPeriod = parseFloat(formData.amount as string) / periodCount;

                  return (
                    <>
                      <span>
                        {formatPeriod(formData.startPeriod)} to {formatPeriod(formData.endPeriod)}
                      </span>
                      <div>
                        {periodCount} {isMonthly ? 'months' : 'quarters'} × ${amountPerPeriod.toFixed(2)} = ${parseFloat(formData.amount as string).toFixed(2)}
                      </div>
                    </>
                  );
                })()}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Modified layout to position buttons next to the notes section in a horizontal arrangement */}
      <div className="flex flex-col md:flex-row gap-5">
        {/* Notes & Attachments section - takes up more space */}
        <div className="flex-1">
          <details className="group" open={isNotesOpen} onToggle={() => setIsNotesOpen(!isNotesOpen)}>
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
                {/* IMPROVED: Document Feature Button with Message */}
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="absolute right-2 bottom-2 opacity-80 hover:opacity-100"
                  onClick={handleAttachFile}
                  title="Attach a file (coming soon)"
                >
                  <Paperclip className="h-4 w-4" />
                  <span className="sr-only">Attach file (coming soon)</span>
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
          <Button type="submit" disabled={isSubmitting || !!validationError}>
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                {isEditing ? "Updating..." : "Submitting..."}
              </>
            ) : (
              isEditing ? "Update" : "Submit"
            )}
          </Button>
        </div>
      </div>
    </form>
  )
}
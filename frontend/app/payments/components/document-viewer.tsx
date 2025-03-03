"use client"

import { useState } from "react"
import { X, FileText, Maximize2, Minimize2 } from "lucide-react"
import { Button } from "@/components/ui/button"

interface DocumentViewerProps {
  documentUrl?: string | null;
  documentName?: string;
  onClose?: () => void;
  className?: string;
}

export function DocumentViewer({ documentUrl, documentName, onClose, className }: DocumentViewerProps) {
  if (!documentUrl) {
    return (
      <div className={`flex items-center justify-center h-full bg-gray-50 rounded-lg border border-dashed border-gray-300 p-12 ${className || ''}`}>
        <div className="text-center">
          <p className="text-sm text-gray-500">No document selected</p>
          {onClose && (
            <button 
              onClick={onClose}
              className="mt-2 text-sm text-blue-500 hover:text-blue-700"
            >
              Close
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className={`h-full ${className || ''}`}>
      <div className="bg-gray-100 p-2 border-b flex justify-between items-center">
        <h3 className="text-sm font-medium">{documentName || "Document"}</h3>
        {onClose && (
          <button 
            onClick={onClose}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            Close
          </button>
        )}
      </div>
      <iframe 
        src={documentUrl} 
        className="w-full h-[calc(100%-2rem)]" 
        title={documentName || "Document Viewer"}
      />
    </div>
  );
}


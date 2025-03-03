"use client"

import { useState } from "react"
import { X, FileText, Maximize2, Minimize2 } from "lucide-react"
import { Button } from "@/components/ui/button"

interface DocumentViewerProps {
  documentUrl: string | null
  onClose: () => void
  className?: string
}

export function DocumentViewer({ documentUrl, onClose, className = "" }: DocumentViewerProps) {
  const [isFullScreen, setIsFullScreen] = useState(false)

  const toggleFullScreen = () => {
    setIsFullScreen(!isFullScreen)
  }

  return (
    <div
      className={`border-l border-gray-200 bg-white flex flex-col h-full ${className} ${
        isFullScreen ? "fixed inset-0 z-50" : ""
      }`}
    >
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <h2 className="text-lg font-medium text-gray-800">Document Preview</h2>
        <div className="flex items-center space-x-2">
          <Button variant="ghost" size="icon" onClick={toggleFullScreen}>
            {isFullScreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
          </Button>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="flex-grow p-4">
        <div className="bg-gray-100 rounded-md p-4 h-full flex items-center justify-center">
          {documentUrl ? (
            <div className="text-center">
              <FileText className="h-16 w-16 mx-auto mb-4 text-gray-400" />
              <p className="text-sm text-gray-500 mb-4">Document Preview</p>
              <p className="text-xs text-gray-400 mb-4">In a real application, the PDF would be rendered here</p>
              <p className="text-sm font-medium text-gray-700 mb-4">{documentUrl.split("/").pop()}</p>
              <Button size="sm" variant="outline" onClick={toggleFullScreen}>
                {isFullScreen ? "Exit Full Screen" : "View Full Screen"}
              </Button>
            </div>
          ) : (
            <p className="text-gray-500">No document selected</p>
          )}
        </div>
      </div>
    </div>
  )
}


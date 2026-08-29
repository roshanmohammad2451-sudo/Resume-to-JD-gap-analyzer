import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, Loader2, X, RefreshCw } from 'lucide-react';

export const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
};

interface PDFDropzoneProps {
  id: string;
  label?: string;
  sublabel?: string;
  accept?: string;
  maxSizeMB?: number;
  currentFile: File | null;
  isLoading: boolean;
  loadingText?: string;
  onFileSelected: (file: File) => void;
  onError?: (errorMessage: string) => void;
  onClear?: () => void;
  accentColor?: 'cyan' | 'blue';
  disabled?: boolean;
}

export const PDFDropzone: React.FC<PDFDropzoneProps> = ({
  id,
  label = 'Click to select or drag PDF file here',
  sublabel = 'Supports PDF format only (Max 10MB)',
  accept = '.pdf,application/pdf',
  maxSizeMB = 10,
  currentFile,
  isLoading,
  loadingText = 'Extracting PDF text page by page...',
  onFileSelected,
  onError,
  onClear,
  accentColor = 'cyan',
  disabled = false,
}) => {
  const [isDragOver, setIsDragOver] = useState<boolean>(false);
  const dragCounter = useRef<number>(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const isCyan = accentColor === 'cyan';
  const activeBorderClass = isCyan
    ? 'border-cyan-400 bg-cyan-950/40 ring-4 ring-cyan-500/20 scale-[1.01]'
    : 'border-blue-400 bg-blue-950/40 ring-4 ring-blue-500/20 scale-[1.01]';
  const iconColorClass = isCyan ? 'text-cyan-400' : 'text-blue-400';
  const buttonClass = isCyan
    ? 'bg-cyan-600 hover:bg-cyan-500 shadow-cyan-600/20'
    : 'bg-blue-600 hover:bg-blue-500 shadow-blue-600/20';

  const validateAndProcessFile = (file: File) => {
    // 1. Validate PDF format
    const isPdf =
      file.name.toLowerCase().endsWith('.pdf') ||
      file.type === 'application/pdf' ||
      file.type === 'application/x-pdf';

    if (!isPdf) {
      onError?.(`Unsupported file format "${file.name}". Only PDF documents (.pdf) are accepted.`);
      return;
    }

    // 2. Validate Size Limit
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      onError?.(
        `File "${file.name}" (${formatFileSize(file.size)}) exceeds the maximum allowed size of ${maxSizeMB}MB.`
      );
      return;
    }

    // 3. Clear errors and pass file to callback
    onFileSelected(file);
  };

  const handleDragEnter = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (disabled || isLoading) return;

    dragCounter.current += 1;
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDragOver(true);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (disabled || isLoading) return;
    e.dataTransfer.dropEffect = 'copy';
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (disabled || isLoading) return;

    dragCounter.current -= 1;
    if (dragCounter.current <= 0) {
      dragCounter.current = 0;
      setIsDragOver(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current = 0;
    setIsDragOver(false);

    if (disabled || isLoading) return;

    const files = e.dataTransfer.files;
    if (!files || files.length === 0) return;

    if (files.length > 1) {
      onError?.('Please drop exactly one PDF file at a time.');
      return;
    }

    validateAndProcessFile(files[0]);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndProcessFile(e.target.files[0]);
      // Reset input value so re-selecting same file works
      e.target.value = '';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if ((e.key === 'Enter' || e.key === ' ') && !isLoading && !disabled) {
      e.preventDefault();
      fileInputRef.current?.click();
    }
  };

  return (
    <div
      role="region"
      aria-label={label}
      tabIndex={disabled || isLoading ? -1 : 0}
      onKeyDown={handleKeyDown}
      onDragEnter={handleDragEnter}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`border-2 border-dashed rounded-xl p-6 text-center transition-all relative outline-none select-none ${
        isDragOver
          ? activeBorderClass
          : 'border-slate-800 hover:border-slate-700 bg-slate-900/40 focus-visible:ring-2 focus-visible:ring-cyan-500/50'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      onClick={() => {
        if (!isLoading && !disabled) {
          fileInputRef.current?.click();
        }
      }}
    >
      <input
        ref={fileInputRef}
        type="file"
        id={id}
        accept={accept}
        className="hidden"
        disabled={disabled || isLoading}
        onChange={handleInputChange}
      />

      {isLoading ? (
        <div className="py-8 flex flex-col items-center justify-center space-y-3 pointer-events-none">
          <Loader2 className={`w-8 h-8 ${iconColorClass} animate-spin`} />
          <p className="text-sm font-medium text-slate-300">{loadingText}</p>
        </div>
      ) : isDragOver ? (
        <div className="py-8 flex flex-col items-center justify-center space-y-2 pointer-events-none animate-in fade-in duration-200">
          <div className="p-3 rounded-full bg-slate-800/90 text-white mb-1 shadow-lg">
            <UploadCloud className={`w-9 h-9 ${iconColorClass} animate-bounce`} />
          </div>
          <p className={`text-base font-bold ${isCyan ? 'text-cyan-300' : 'text-blue-300'}`}>
            Drop PDF File Here
          </p>
          <p className="text-xs text-slate-400">Release to start instant text extraction</p>
        </div>
      ) : currentFile ? (
        <div 
          className="flex flex-col items-center justify-center min-h-[140px] space-y-3"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="p-3 rounded-full bg-slate-800/80 text-slate-400 mb-1">
            <FileText className={`w-8 h-8 ${iconColorClass}`} />
          </div>
          <div className="text-center max-w-full px-4">
            <p className="text-sm font-bold text-slate-200 truncate max-w-xs sm:max-w-md mx-auto" title={currentFile.name}>
              {currentFile.name}
            </p>
            <p className="text-xs text-slate-500 mt-0.5">
              {formatFileSize(currentFile.size)} • PDF Document
            </p>
          </div>

          <div className="flex items-center space-x-2 pt-2">
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold text-white transition-all shadow-md inline-flex items-center ${buttonClass}`}
            >
              <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
              Change PDF
            </button>

            {onClear && (
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onClear();
                }}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-400 hover:text-rose-300 hover:bg-rose-950/50 border border-slate-800 hover:border-rose-800 transition-all inline-flex items-center"
              >
                <X className="w-3.5 h-3.5 mr-1" />
                Remove
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center min-h-[140px] pointer-events-none">
          <div className="p-3 rounded-full bg-slate-800/80 text-slate-400 mb-3">
            <UploadCloud className={`w-8 h-8 ${iconColorClass}`} />
          </div>
          <p className="text-sm font-medium text-slate-200 mb-1">
            {label}
          </p>
          <p className="text-xs text-slate-500 mb-4">
            {sublabel}
          </p>
          <button
            type="button"
            className={`pointer-events-auto px-4 py-2 rounded-lg text-xs font-semibold text-white transition-all shadow-lg ${buttonClass}`}
            onClick={(e) => {
              e.stopPropagation();
              fileInputRef.current?.click();
            }}
          >
            Select PDF File
          </button>
        </div>
      )}
    </div>
  );
};

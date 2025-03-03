"use client"





import { useState } from "react"


import { Search, Building, UserCheck, UserX, UserCog } from "lucide-react"


import { Input } from "@/components/ui/input"


import { ScrollArea } from "@/components/ui/scroll-area"


import { Switch } from "@/components/ui/switch"


import { Button } from "@/components/ui/button"
import type { Client } from "../../../types"





interface ClientSidebarProps {


  clients: Client[]


  selectedClient: Client | null


  onSelectClient: (client: Client) => void


}





export function ClientSidebar({ clients, selectedClient, onSelectClient }: ClientSidebarProps) {


  const [searchQuery, setSearchQuery] = useState("")


  const [isProviderView, setIsProviderView] = useState(false)


  const [expandedProvider, setExpandedProvider] = useState<string | null>(null)





  const filteredClients = clients.filter((client) => client.name.toLowerCase().includes(searchQuery.toLowerCase()))





  const providers = Array.from(new Set(clients.map((client) => client.planProvider)))





  const toggleProvider = (provider: string) => {


    setExpandedProvider(expandedProvider === provider ? null : provider)


  }





  const getComplianceIcon = (status: string) => {


    switch (status) {


      case "Compliant":


        return <UserCheck className="h-4 w-4 text-green-500" />


      case "Review Needed":


        return <UserCog className="h-4 w-4 text-yellow-500" />


      case "Payment Overdue":


        return <UserX className="h-4 w-4 text-red-500" />


      default:


        return <UserCheck className="h-4 w-4 text-gray-400" />


    }


  }





  return (


    <div className="w-80 border-r border-gray-200 bg-white flex flex-col h-full">


      <div className="p-4 border-b border-gray-200">


        <h2 className="text-xl font-semibold text-gray-800 mb-4">Clients</h2>


        <div className="relative mb-4">


          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />


          <Input


            type="search"


            placeholder="Search clients..."


            className="pl-10 bg-gray-50"


            value={searchQuery}


            onChange={(e) => setSearchQuery(e.target.value)}


          />


        </div>


        <div className="flex items-center justify-between">


          <span className="text-sm font-medium text-gray-700">View by Provider</span>


          <Switch


            checked={isProviderView}


            onCheckedChange={(checked) => {


              setIsProviderView(checked)


              setExpandedProvider(null)


            }}


          />


        </div>


      </div>





      <ScrollArea className="flex-1">


        <div className="p-2">


          {isProviderView


            ? providers.map((provider) => (


                <div key={provider} className="mb-2">


                  <Button


                    variant="ghost"


                    className="w-full justify-between py-2 px-3 hover:bg-gray-100"


                    onClick={() => toggleProvider(provider)}


                  >


                    <span className="font-medium">{provider}</span>


                    <Building className="h-4 w-4 text-gray-500" />


                  </Button>


                  {expandedProvider === provider && (


                    <div className="ml-4 mt-1">


                      {filteredClients


                        .filter((client) => client.planProvider === provider)


                        .map((client) => (


                          <ClientButton


                            key={client.id}


                            client={client}


                            isSelected={selectedClient?.id === client.id}


                            onClick={() => onSelectClient(client)}


                          />


                        ))}


                    </div>


                  )}


                </div>


              ))


            : filteredClients.map((client) => (


                <ClientButton


                  key={client.id}


                  client={client}


                  isSelected={selectedClient?.id === client.id}


                  onClick={() => onSelectClient(client)}


                />


              ))}


        </div>


      </ScrollArea>


    </div>


  )


}





interface ClientButtonProps {


  client: Client


  isSelected: boolean


  onClick: () => void


}





function ClientButton({ client, isSelected, onClick }: ClientButtonProps) {


  const getComplianceIcon = (status: string) => {


    switch (status) {


      case "Compliant":


        return <UserCheck className="h-4 w-4 text-green-500" />


      case "Review Needed":


        return <UserCog className="h-4 w-4 text-yellow-500" />


      case "Payment Overdue":


        return <UserX className="h-4 w-4 text-red-500" />


      default:


        return <UserCheck className="h-4 w-4 text-gray-400" />


    }


  }





  return (


    <Button


      variant="ghost"


      className={`w-full justify-start py-2 px-3 mb-1 ${isSelected ? "bg-gray-100" : ""}`}


      onClick={onClick}


    >


      <div className="flex items-center w-full">


        <span className="mr-3">{getComplianceIcon(client.complianceStatus)}</span>


        <span className="truncate flex-grow text-left">{client.name}</span>


      </div>


    </Button>


  )


}






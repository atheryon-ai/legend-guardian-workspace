@description('Location for all resources')
param location string = 'eastus'

@description('AKS cluster name')
param aksClusterName string = 'aks-legend'

@description('ACR name (must be globally unique)')
param acrName string = 'acrlegend${uniqueString(resourceGroup().id)}'

@description('Admin password for MongoDB')
@secure()
param mongoAdminPassword string

// Azure Container Registry
resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

// AKS Cluster
resource aks 'Microsoft.ContainerService/managedClusters@2023-11-01' = {
  name: aksClusterName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    kubernetesVersion: '1.28.0'
    dnsPrefix: aksClusterName
    agentPoolProfiles: [
      {
        name: 'nodepool1'
        count: 2
        vmSize: 'Standard_DS2_v2'
        osType: 'Linux'
        mode: 'System'
        enableAutoScaling: true
        minCount: 1
        maxCount: 5
      }
    ]
    networkProfile: {
      networkPlugin: 'azure'
      networkPolicy: 'azure'
      serviceCidr: '10.0.0.0/16'
      dnsServiceIP: '10.0.0.10'
    }
  }
}

// Role assignment for AKS to pull from ACR
resource acrPullRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aks.id, acr.id, '7f951dda-4ed3-4680-a7ca-43fe0d0b9a7f')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe0d0b9a7f')
    principalId: aks.properties.identityProfile.kubeletidentity.objectId
    principalType: 'ServicePrincipal'
  }
}

// Outputs
output acrLoginServer string = acr.properties.loginServer
output acrName string = acr.name
output aksClusterName string = aks.name
output resourceGroupName string = resourceGroup().name
